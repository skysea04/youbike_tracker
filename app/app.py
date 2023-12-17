import logging
import threading
import time
from dataclasses import dataclass, field

import constants
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
# Configure logging
logging.basicConfig(filename='info.log', level=logging.INFO)


@dataclass
class BikeSystem:
    system: str
    data: dict[str, dict]
    sna_map: dict[str, str]
    page_urls: list[str] = field(default_factory=list)
    url: list[str] = field(default_factory=list)


YOUBIKE = BikeSystem(
    system='1',
    data={},
    sna_map={},
    page_urls=[constants.XINBEI_YOUBIKE_URL],
)

YOUBIKE2 = BikeSystem(
    system='2',
    data={},
    sna_map={},
    page_urls=[constants.XINBEI_YOUBIKE2_URL],
    url=[constants.TAIPEI_YOUBIKE2_URL],
)


SYNC_INTERVAL = 180


def get_data_by_page_url(bike_system: BikeSystem, page_url: str):
    page = 0
    size = 200
    err_cnt = 0
    while err_cnt < 3:
        try:
            params = {
                'page': page,
                'size': size,
            }
            resp = requests.get(page_url, params=params, timeout=10).json()
            if not resp:
                break

            bike_system.data.update({station['sno']: station for station in resp})
            bike_system.sna_map.update({station['sna']: station['sno'] for station in resp})
            page += 1

        except Exception as e:
            err_cnt += 1
            logging.error('Get data error | url: %s | params: %s | error: %s', page_url, params, e)
            time.sleep(3)


def get_data_by_url(bike_system: BikeSystem, url: str):
    try:
        resp = requests.get(url, timeout=10).json()
        if not resp:
            raise Exception('Url response is empty')

        bike_system.data.update({station['sno']: station for station in resp})
        bike_system.sna_map.update({station['sna']: station['sno'] for station in resp})

    except Exception as e:
        logging.error('Get data error | url: %s | error: %s', url, e)


def get_all_stations_info(bike_system: BikeSystem):
    for page_url in bike_system.page_urls:
        get_data_by_page_url(bike_system, page_url)

    for url in bike_system.url:
        get_data_by_url(bike_system, url)


def sync_bike_resource():
    while True:
        get_all_stations_info(YOUBIKE)
        get_all_stations_info(YOUBIKE2)
        time.sleep(SYNC_INTERVAL)


@app.route('/sno', methods=['GET'])
def get_station_sno():
    """Get station sno by station name

    Request:
        system: str (1 or 2)
        name: str

    Response:
        name(sna): str(sno)
    """
    system = request.args.get('system')

    name = request.args.get('name')
    if not name or not system:
        return jsonify({'error': 'Bad Request'}), 400

    system = YOUBIKE if system == YOUBIKE.system else YOUBIKE2

    sna_map = {}
    for sna, sno in system.sna_map.items():
        if name in sna:
            sna_map[sna] = sno

    return jsonify(sna_map)


@app.route('/track/sno', methods=['GET'])
def get_availability_by_sno():
    """Get the available bikes and parking spaces between two stations

    Request:
        system: str (1 or 2)
        depart: str
        arrive: str

    Response:
        can_borrow: int
        can_park: int
        actual_available: int
    """
    system = request.args.get('system')
    depart = request.args.get('depart')
    arrive = request.args.get('arrive')

    if not system or not depart or not arrive:
        return jsonify({'error': 'Bad Request'}), 400

    system = YOUBIKE if system == YOUBIKE.system else YOUBIKE2
    depart_info = system.data.get(depart)
    arrive_info = system.data.get(arrive)

    if not depart_info:
        return jsonify({f'error': 'depart station {depart} not found'}), 404

    if not arrive_info:
        return jsonify({f'error': 'arrive station {arrive} not found'}), 404

    return jsonify({
        'can_borrow': int(depart_info['sbi']),
        'can_park': int(arrive_info['bemp']),
        'actual_available': min(int(depart_info['sbi']), int(arrive_info['bemp'])),
    })


@app.route('/track/name', methods=['GET'])
def get_availability_by_name():
    """Get the available bikes and parking spaces between two stations

    Request:
        system: str (1 or 2)
        depart: str
        arrive: str

    Response:
        can_borrow: int
        can_park: int
        actual_available: int
    """
    system = request.args.get('system')
    depart = request.args.get('depart')
    arrive = request.args.get('arrive')

    if not system or not depart or not arrive:
        return jsonify({'error': 'Bad Request'}), 400

    system = YOUBIKE if system == YOUBIKE.system else YOUBIKE2
    depart_info = system.data.get(system.sna_map.get(depart, ''))
    arrive_info = system.data.get(system.sna_map.get(arrive, ''))

    if not depart_info:
        return jsonify({f'error': 'depart station {depart} not found'}), 404

    if not arrive_info:
        return jsonify({f'error': 'arrive station {arrive} not found'}), 404

    return jsonify({
        'can_borrow': int(depart_info['sbi']),
        'can_park': int(arrive_info['bemp']),
        'actual_available': min(int(depart_info['sbi']), int(arrive_info['bemp'])),
    })


@app.route('/', methods=['GET'])
def index():
    return 'This is a Youbike tracker'


threading.Thread(target=sync_bike_resource).start()

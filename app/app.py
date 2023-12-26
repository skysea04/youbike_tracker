import traceback
from functools import wraps

from flask import Flask, jsonify, request
from services import YOUBIKE, YOUBIKE2

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def catch_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    return wrapper


@app.route('/sno', methods=['GET'])
@catch_exceptions
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
    system.get_all_stations_info()

    sna_map = {}
    for sna, sno in system.sna_map.items():
        if name in sna:
            sna_map[sna] = sno

    return jsonify(sna_map)


@app.route('/track/sno', methods=['GET'])
@catch_exceptions
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
    system.get_all_stations_info()
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
@catch_exceptions
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
    system.get_all_stations_info()
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

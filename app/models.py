import time
import traceback
from dataclasses import dataclass, field

import requests
from utils import class_local_cache


@dataclass
class BikeSystem:
    system: str
    data: dict = field(default_factory=dict)
    sna_map: dict = field(default_factory=dict)
    page_urls: list[str] = field(default_factory=list)
    url: list[str] = field(default_factory=list)

    def __str__(self):
        return 'Youbike' + self.system

    def _get_data_by_page_url(self, page_url: str):
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

                self.data.update({station['sno']: station for station in resp})
                self.sna_map.update({station['sna']: station['sno'] for station in resp})
                page += 1

            except Exception:
                traceback.print_exc()
                err_cnt += 1
                time.sleep(1)

    def _get_data_by_url(self, url: str):
        resp = requests.get(url, timeout=10).json()
        if not resp:
            raise Exception('Url response is empty')

        self.data.update({station['sno']: station for station in resp})
        self.sna_map.update({station['sna']: station['sno'] for station in resp})

    @class_local_cache()
    def get_all_stations_info(self):
        for page_url in self.page_urls:
            self._get_data_by_page_url(page_url)

        for url in self.url:
            self._get_data_by_url(url)

        return self

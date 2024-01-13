import asyncio
from dataclasses import dataclass, field
from typing import Coroutine, Optional

from aiohttp import ClientSession
from utils import async_run_tasks, class_local_cache


@dataclass
class BikeSystem:
    system: str
    data: dict = field(default_factory=dict)
    sna_map: dict = field(default_factory=dict)
    page_urls: list[str] = field(default_factory=list)
    url: list[str] = field(default_factory=list)

    def __str__(self):
        return 'Youbike' + self.system

    async def get_data_by_page_url(self, page_url: str) -> list[Coroutine]:
        return [
            self.get_data_by_url(page_url, page)
            for page in range(0, 10)
        ]

    async def get_data_by_url(self, url: str, page: Optional[int] = None, size: int = 200):
        params = {}
        if page is not None:
            params = {'page': page, 'size': size}

        async with ClientSession() as sess:
            async with sess.get(url, params=params) as resp:
                resp = await resp.json()
                if not resp:
                    return

                self.data.update({station['sno']: station for station in resp})
                self.sna_map.update({station['sna']: station['sno'] for station in resp})

    @class_local_cache()
    def get_all_stations_info(self):
        tasks = []

        for page_url in self.page_urls:
            tasks.extend(
                self.get_data_by_url(page_url, page) for page in range(0, 5)
            )

        for url in self.url:
            tasks.append(self.get_data_by_url(url))

        asyncio.run(async_run_tasks(tasks))

        return self

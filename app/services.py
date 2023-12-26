from models import BikeSystem

# Station APIs
XINBEI_YOUBIKE_URL = 'https://data.ntpc.gov.tw/api/datasets/71cd1490-a2df-4198-bef1-318479775e8a/json'
XINBEI_YOUBIKE2_URL = 'https://data.ntpc.gov.tw/api/datasets/010e5b15-3823-4b20-b401-b1cf000550c5/json'

TAIPEI_YOUBIKE2_URL = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'


YOUBIKE = BikeSystem(
    system='1',
    page_urls=[XINBEI_YOUBIKE_URL],
)

YOUBIKE2 = BikeSystem(
    system='2',
    page_urls=[XINBEI_YOUBIKE2_URL],
    url=[TAIPEI_YOUBIKE2_URL],
)

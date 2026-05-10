# 東海道新幹線（東京〜新大阪）の駅順（のぞみ停車駅ベース・旅客案内でよく使う並び）

TOKAIDO_STATIONS = [
    {"id": "tokyo", "name": "東京"},
    {"id": "shinagawa", "name": "品川"},
    {"id": "shin_yokohama", "name": "新横浜"},
    {"id": "odawara", "name": "小田原"},
    {"id": "atami", "name": "熱海"},
    {"id": "mishima", "name": "三島"},
    {"id": "shin_fuji", "name": "新富士"},
    {"id": "shizuoka", "name": "静岡"},
    {"id": "hamamatsu", "name": "浜松"},
    {"id": "toyohashi", "name": "豊橋"},
    {"id": "nagoya", "name": "名古屋"},
    {"id": "maibara", "name": "米原"},
    {"id": "kyoto", "name": "京都"},
    {"id": "shin_osaka", "name": "新大阪"},
]


def station_index(station_id: str) -> int:
    for i, s in enumerate(TOKAIDO_STATIONS):
        if s["id"] == station_id:
            return i
    raise ValueError(station_id)


def route_between(origin_id: str, dest_id: str) -> list[dict]:
    o = station_index(origin_id)
    d = station_index(dest_id)
    if o <= d:
        return TOKAIDO_STATIONS[o : d + 1]
    return list(reversed(TOKAIDO_STATIONS[d : o + 1]))

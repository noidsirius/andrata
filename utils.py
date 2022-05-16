import requests
import re
import time
from bs4 import BeautifulSoup
from collections import namedtuple

GPlayData = namedtuple('GPlayData', ['install', 'category', 'rating', 'rate_num'])


def get_gplay_data(package_name: str) -> GPlayData:
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}
    url = f"https://play.google.com/store/apps/details?id={package_name}&hl=en"
    resp = requests.get(url, headers=headers)
    install = rating = rate_num = -1
    category = "UNKNOWN"
    if resp.status_code == 200:
        txt = resp.text
        # rating
        result = re.search(r"Rated ((?:\d\.\d|\d)) stars by ((?:\d+\,\d+,\d+|\d+\,\d+|\d+)) people", txt)
        if result:
            rating_round = result.group(1)
            rating_ppl = int(result.group(2).replace(",", ""))
            result = re.search(fr'\["{rating_round}",((?:\d\.\d+|\d+))\]', txt)
            rating_raw = result.group(1)
            if rating_ppl > 0:
                rating = rating_raw
                rate_num = rating_ppl

        # install
        result = re.search(r'<span class=\"htlgb\">((?:\d+,\d+,\d+|\d+,\d+|\d+))\+</span>', txt)
        if result:
            install_round = result.group(1)
            result = re.search(fr'\["{install_round}\+",\d+,(\d+),"[A-Za-z0-9,]+\+"\]', txt)
            install_raw = result.group(1)
            install = install_raw

        # category
        soup = BeautifulSoup(txt, "html.parser")
        tag = soup.find("a", {"itemprop": "genre"})
        if tag and "href" in tag.attrs and tag["href"]:
            # e.g., href="/store/apps/category/MUSIC_AND_AUDIO"
            cat = tag["href"].split("/")[-1]
            category = cat
    return GPlayData(install, category, rating, rate_num)


if __name__ == "__main__":
    print(get_gplay_data("com.colpit.diamondcoming.isavemoney"))

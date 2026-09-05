"""CifraClub Module"""

import requests
from bs4 import BeautifulSoup

CIFRACLUB_URL = "https://www.cifraclub.com.br/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

class CifraClub():
    """CifraClub Class"""
    def __init__(self):
        pass

    def cifra(self, artist: str, song: str) -> dict:
        """Lê a página HTML e extrai a cifra e meta dados da música."""
        result = {}
        url = f"{CIFRACLUB_URL}{artist}/{song}/"
        result['cifraclub_url'] = url

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code != 200:
                result['error'] = f"Status code: {response.status_code}"
                return result

            soup = BeautifulSoup(response.text, 'html.parser')
            self.get_details(soup, result)
            self.get_cifra(soup, result)
        except Exception as err: # pylint: disable=broad-except
            result['error'] = str(err)

        return result

  def get_details(self, soup: BeautifulSoup, result: dict):
        """Obtêm os meta dados da música"""
        t1 = soup.find('h1', class_='t1') or soup.find('h1')
        result['name'] = t1.text.strip() if t1 else ""

        artist_elem = (
            soup.find('h2', class_='t3')
            or soup.find('span', class_='cifra-artist')
            or soup.select_one('div.cifra header h2 a')
            or soup.select_one('div.cifra header h2')
            or soup.select_one('h1.t1 + h2')
        )
        result['artist'] = artist_elem.text.strip() if artist_elem else ""

        cifra_tom = soup.find(id='cifra_tom')
        if cifra_tom and cifra_tom.find('a'):
            result['key'] = cifra_tom.find('a').text.strip()

        placeholder = soup.find('div', class_='player-placeholder')
        if placeholder and placeholder.find('img'):
            img_youtube = placeholder.img.get('src', '')
            if '/vi/' in img_youtube:
                cod = img_youtube.split('/vi/')[1].split('/')[0]
                result['youtube_url'] = f"https://www.youtube.com/watch?v={cod}"

    def get_cifra(self, soup: BeautifulSoup, result: dict):
        """Obtêm a cifra da música e converte para json"""
        cifra_cnt = soup.find('div', class_='cifra_cnt')
        if cifra_cnt and cifra_cnt.find('pre'):
            result['cifra'] = cifra_cnt.find('pre').text.split('\n')
        else:
            pre = soup.find('pre')
            result['cifra'] = pre.text.split('\n') if pre else []

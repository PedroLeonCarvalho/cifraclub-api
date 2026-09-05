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
            self.get_details(soup, result, default_artist=artist)
            self.get_cifra(soup, result)
        except Exception as err:  # pylint: disable=broad-except
            result['error'] = str(err)

        return result

    def get_details(self, soup: BeautifulSoup, result: dict, default_artist: str = ""):
        """Obtêm os meta dados da música"""
        # Título da música
        t1 = (
            soup.find('h1', class_='t1')
            or soup.select_one('div.cifra header h1')
            or soup.find('h1')
        )
        result['name'] = t1.text.strip() if t1 else ""

        # Nome do artista
        artist_elem = (
            soup.find('a', class_='cifra-artist')
            or soup.select_one('div.cifra header a')
            or soup.select_one('div.cifra header h2')
            or soup.select_one('h2.t3')
            or soup.find('meta', property='og:music:musician')
        )

        if artist_elem:
            if artist_elem.name == 'meta':
                result['artist'] = artist_elem.get('content', '').strip()
            else:
                result['artist'] = artist_elem.text.strip()
        else:
            # Fallback limpo a partir do slug (ex: "coldplay" -> "Coldplay")
            result['artist'] = default_artist.replace('-', ' ').title()

        # Tom original
        cifra_tom = soup.find(id='cifra_tom')
        if cifra_tom and cifra_tom.find('a'):
            result['key'] = cifra_tom.find('a').text.strip()

        # YouTube
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

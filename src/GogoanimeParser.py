import googlesearch
from bs4 import BeautifulSoup
import requests
import json

class GogoanimeParser:
    
    def __init__(self) -> None:
        self.__websiteUrl = self.__readWebsiteUrlFromFile()

    ################# A P I ####################
    def getLatestEpisode(self, animeTitle: str):
        animeTitle = self.__urlifyAnimeTitle(animeTitle)
        response = self.__makeGetRequest(animeTitle)
        if not self.__requestIsSuccessful(response, animeTitle):
            return None
        latestEpisode = self.__parseWebsite(response)
        if latestEpisode == None:
            return None
        else:
            return latestEpisode

    def getLatestEpisodeUrl(self, animeTitle: str, episodeNumber: int):
        animeTitle = self.__urlifyAnimeTitle(animeTitle)
        return f"https://gogoanime.ai/{animeTitle}-episode-{str(episodeNumber)}"

    ################# H E L P E R   M E T H O D S ######################
    def __readWebsiteUrlFromFile(self):
        try:
            with open(r'..\data\website.json', 'r', encoding='utf-8') as jsonFile:
                return json.load(jsonFile)['url']
        except Exception as fileReadingError:
            print('Error occured while reading website.json')
            print(fileReadingError)

    def __removeNonAsciiCharacters(self, animeTitle: str):
        return "".join([ch for ch in animeTitle if 0 <= ord(ch) <= 126])

    def __urlifyAnimeTitle(self, animeTitle: str):
        # GoGoAnime urls have the following format: https://gogoanime.ai/category/shingeki-no-kyojin
        # Any spaces in the anime title need to be replaced with '-' and also delete any special characters
        # or non-ASCII characters.
        animeTitle = self.__removeNonAsciiCharacters(animeTitle).strip()
        specialCharacters = "!@#$%^&*()[]}{;:,./<>?\|`~-=_+"
        return "-".join(animeTitle.translate({ord(c): "" for c in specialCharacters}).split(' ')).lower()

    def __makeGetRequest(self, animeTitle: str):
        try:
            # Url format example: https://gogoanime.ai/category/shingeki-no-kyojin
            response = requests.get(f"{self.__websiteUrl}/category/{animeTitle}")
            if response.status_code == 404:
                return self.__searchGoogleForValidUrl(animeTitle)
            return response
        except Exception as httpGetRequestError:
            print(f'Failed to make GET request to {self.__websiteUrl}/category/{animeTitle}')
            print(httpGetRequestError)
            return None

    def __searchGoogleForValidUrl(self, animeTitle: str):
        for url in googlesearch.search(f'gogoanime.ai {animeTitle}', stop=1):
            return requests.get(url).url

    def __requestIsSuccessful(self, response, animeTitle: str):
        if response == None:
            return False
        if response.status_code != 200:
            print(f'Failed to make GET request to {self.__websiteUrl}/category/{animeTitle}')
            print(f'Response status code: {response.status_code}')
            return False
        return True

    def __getWebsiteHtml(self, response: requests.Response):
        try:
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as parsingError:
            print('An error has occured while parsing html...')
            print(parsingError)
            return None

    def __findLastEpisode(self, html: BeautifulSoup):
        for a in html.find_all('a', attrs={'class': 'active'}):
            return int(a.get('ep_end'))

    def __parseWebsite(self, response: requests.Response):
        websiteHtml = self.__getWebsiteHtml(response)
        if websiteHtml == None:
            return None
        lastEpisode = self.__findLastEpisode(websiteHtml)
        if lastEpisode == None:
            return None
        else:
            return lastEpisode

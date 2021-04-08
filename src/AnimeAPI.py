from youtubesearchpython import SearchVideos
from GogoanimeParser import GogoanimeParser
from DatetimeParser import DatetimeParser
from jikanpy import Jikan
import json

class AnimeAPI(Jikan):
    
    def __init__(self) -> None:
        super().__init__()

    ################### A P I #######################
    def getInfo(self, query: str):
        animeId = self.__getAnimeId(query)
        if animeId == None:
            return None
        info = self.__getAnimeInfoDict(animeId)
        return self.__getInfoToShow(info)

    def getLatestEpisode(self, animeTitle: str):
        latestEpisode = GogoanimeParser().getLatestEpisode(animeTitle)
        if latestEpisode == None:
            return None
        else:
            return latestEpisode

    def getLatestEpisodeUrl(self, animeTitle: str, episodeNumber: int):
        return GogoanimeParser().getLatestEpisodeUrl(animeTitle, episodeNumber)

    def getNotificationInfo(self, info: dict):
        latestEpisode = self.getLatestEpisode(info['title'])
        if latestEpisode == None:
            return None
        else:
            return {
                "title": info['title'],
                "currentEpisode": latestEpisode,
                "episodes": info['episodes'],
                "broadcast": info['broadcast']
            }

    def getTrailer(self, animeTitle: str):
        youtubeResult = SearchVideos(f'{animeTitle} 1st trailer', max_results=1).result()
        youtubeResultToDict = json.loads(youtubeResult)
        return youtubeResultToDict['search_result'][0]['link']
    
    def getLatestEpisodeTitle(self, animeTitle, episodeNumber: int):
        try:
            animeId = self.__getAnimeId(animeTitle)
            episode = self.anime(animeId, extension='episodes')['episodes'][-1]
            if episode['episode_id'] == episodeNumber:
                return episode['title']
            else:
                return None
        except Exception as episodeTitleFetchingError:
            print(f'Error occured while getting the title of the latest {animeTitle} episode...')
            print(episodeTitleFetchingError)
            return None

    def getBroadcastRemainingTime(self, animeTitle: str):
        animeInfo = self.getInfo(animeTitle)
        if animeInfo == None:
            return None
        if animeInfo['status'] != 'Currently Airing':
            return 'Not airing'
        try:
            return {
                "anime": animeInfo['title'],
                "broadcast": DatetimeParser().getTimeLeftForBroadcast(animeInfo['broadcast']),
                "episode": self.getLatestEpisode(animeInfo['title']) + 1
            }
        except Exception as datetimeError:
            print('Error occured while getting remaining broadcast time...')
            print(datetimeError)
            return None

    ################## H E L P E R   M E T H O D S ####################
    def __getAnimeId(self, query: str):
        try:
            return self.search('anime', query)['results'][0]['mal_id']
        except Exception as jikanApiError:
            print(f"Error occured while fetching info from Jikan API")
            print(jikanApiError)
            return None

    def __getAnimeInfoDict(self, animeId: int):
        return self.anime(animeId)

    def __getInfoToShow(self, info: dict):
        return {
            "title": info['title'], "type": info['type'], "source": info['source'], "episodes": info['episodes'], "status": info['status'],
            "studio": info['studios'][0]['name'], "premiered": info['premiered'], "score": info['score'], "rank": info['rank'],
            "broadcast": info['broadcast'], "aired": info['aired'], "image_url": info['image_url'], "url": info['url'],
            # Since discord doesn't allow value fields in embeds to be more that 1024 characters, we have to check if synopsis exceeds that...
            "synopsis": info['synopsis'] if len(info['synopsis']) <= 1024 else info['synopsis'][:1020] + '...',
            "mal_image": 'https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPAiC8a86sHufn_jOI-JGtoCQ',
            "genre": ", ".join([genre['name'] for genre in info['genres']]),
        }

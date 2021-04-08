import json

class JsonDatabase:
    
    def __init__(self) -> None:
        self.__serversDb = {}
        self.__animeDb = {}

    ################# A P I ##################
    def animeIsInDatabase(self, serverName: str, animeTitle: str):
        self.__readDatabase()
        for server in self.__animeDb['servers']:
            if server['name'] == serverName:
                for anime in server['anime']:
                    if anime['title'] == animeTitle:
                        return True
                return False

    def addToDatabase(self, serverName: str, animeInfo: dict):
        self.__readDatabase()
        for serverIndex, server in enumerate(self.__animeDb['servers']):
            if server['name'] == serverName:
                self.__animeDb['servers'][serverIndex]['anime'].append(animeInfo)
                self.__writeToAnimeDb()
                return

    def deleteFromDatabase(self, serverName: str, animeTitle: str):
        self.__readDatabase()
        for serverIndex, server in enumerate(self.__animeDb['servers']):
            if server['name'] == serverName:
                for animeIndex, anime in enumerate(server['anime']):
                    if anime['title'] == animeTitle:
                        self.__animeDb['servers'][serverIndex]['anime'].pop(animeIndex)
                        self.__writeToAnimeDb()
                        return

    def getAnimeFromDatabase(self, serverName: str):
        self.__readDatabase()
        for server in self.__animeDb['servers']:
            if server['name'] == serverName:
                return server['anime']

    def addServerToDatabase(self, serverName: str):
        self.__readDatabase()
        self.__serversDb['servers'].append(serverName)
        self.__animeDb['servers'].append({
            "name": serverName,
            "anime": []
        })
        self.__writeToServersDb()
        self.__writeToAnimeDb()

    def updateAnimeEntry(self, animeDb: dict):
        self.__animeDb = animeDb
        self.__writeToAnimeDb()

    def getAnimeDb(self):
        self.__readDatabase()
        return self.__animeDb

    def getServerDb(self):
        self.__readDatabase()
        return self.__serversDb

    ################# H E L P E R   M E T H O D S ##################
    def __readDatabase(self):
        self.__serversDb = self.__readServersDb()
        self.__animeDb = self.__readAnimeDb()

    def __readServersDb(self):
        try:
            with open(r'..\data\servers.json', 'r', encoding='utf-8') as jsonFile:
                return json.load(jsonFile)
        except Exception as fileReadingError:
            print('Error occured while reading server.json')
            print(fileReadingError)
            return None
    
    def __readAnimeDb(self):
        try:
            with open(r'..\data\anime.json', 'r', encoding='utf-8') as jsonFile:
                return json.load(jsonFile)
        except Exception as fileReadingError:
            print('Error occured while reading anime.json')
            print(fileReadingError)
            return None

    def __writeToServersDb(self):
        try:
            with open(r'..\data\servers.json', 'w') as jsonFile:
                json.dump(self.__serversDb, jsonFile, indent=4, ensure_ascii=False)
        except Exception as fileWritingError:
            print('Error occured while writing to servers.json')
            print(fileWritingError)

    def __writeToAnimeDb(self):
        try:
            with open(r'..\data\anime.json', 'w') as jsonFile:
                json.dump(self.__animeDb, jsonFile, indent=4, ensure_ascii=False)
        except Exception as fileWritingError:
            print('Error occured while writing to anime.json')
            print(fileWritingError)
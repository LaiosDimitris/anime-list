from JsonDatabase import JsonDatabase
from AnimeAPI import AnimeAPI
import datetime
import discord
import asyncio
import pytz

class BotCommands:

    def __init__(self) -> None:
        self.animeApi = AnimeAPI()
        self.jsonDatabase = JsonDatabase()

    def anime(self, query: str):
        animeInfo = self.animeApi.getInfo(query)
        if animeInfo == None:
            return None
        self.__discordEmbed = discord.Embed()
        self.__configureEmbed(animeInfo)
        return self.__discordEmbed

    def notify(self, serverName: str, query: str):
        animeInfo = self.animeApi.getInfo(query)
        if animeInfo == None:
            return None
        if self.jsonDatabase.animeIsInDatabase(serverName, animeInfo['title']):
            return 'Already in database', animeInfo
        if animeInfo['status'] != 'Currently Airing':
            return 'Not airing', animeInfo
        notificationInfo = self.animeApi.getNotificationInfo(animeInfo)
        if notificationInfo == None:
            return None
        try:
            self.jsonDatabase.addToDatabase(serverName, notificationInfo)
            return 'Success', self.__getNotifyEmbed(animeInfo)
        except Exception as databaseWritingError:
            print('Error occured while writing to database or getting discord embed...')
            print(databaseWritingError)
            return None

    def delete(self, serverName: str, query: str):
        animeInfo = self.animeApi.getInfo(query)
        if animeInfo == None:
            return None
        if not self.jsonDatabase.animeIsInDatabase(serverName, animeInfo['title']):
            return 'Not in database', animeInfo
        try:
            self.jsonDatabase.deleteFromDatabase(serverName, animeInfo['title'])
            return 'Removed from database successfuly', animeInfo
        except Exception as databaseWritingError:
            return None

    def list(self, serverName: str):
        try:
            animeList = self.jsonDatabase.getAnimeFromDatabase(serverName)
        except Exception as databaseWritingError:
            return None
        if len(animeList) == 0:
            return 'Empty list'
        listEmbed = discord.Embed()
        listEmbed.colour = 0x3be2ff
        for i, anime in enumerate(animeList):
            listEmbed.add_field(name=i+1, value=f"**{anime['title']}** `Episode {anime['currentEpisode']}/{anime['episodes']}`", inline=False)
        return listEmbed

    def trailer(self, query: str):
        animeInfo = self.animeApi.getInfo(query)
        if animeInfo == None:
            return None
        try:
            return self.animeApi.getTrailer(animeInfo['title']), animeInfo
        except Exception as youtubeError:
            print('Error occured searching youtube')
            print(youtubeError)
            return None

    def broadcast(self, query: str):
        time = self.animeApi.getBroadcastRemainingTime(query)
        if time == None:
            return None
        if time == 'Not airing':
            return 'Not airing'
        return time

    async def episodeNotifications(self):
        notifications = []
        while True:
            animeDatabase = self.jsonDatabase.getAnimeDb()
            for serverIndex, server in enumerate(animeDatabase['servers']):
                for animeIndex, anime in enumerate(server['anime']):
                    if self.__getCurrentDayInJapan() in anime['broadcast']:
                        animeLatestEpisode = self.animeApi.getLatestEpisode(anime['title'])
                        if animeLatestEpisode != anime['currentEpisode']:
                            notifications.append(self.__notificationInfo(server['name'], anime, animeLatestEpisode))
                            if animeLatestEpisode == anime['episodes']:
                                self.__removeFinishedAnime(server['name'], anime['title'])
                            else:
                                animeDatabase['servers'][serverIndex]['anime'][animeIndex]['currentEpisode'] = animeLatestEpisode
                                self.__updateLatestEpisode(animeDatabase)         
            if len(notifications) == 0:
                await asyncio.sleep(120)
                continue
            else:
                return notifications

    def addServerToDatabase(self, serverName: str):
        try:
            self.jsonDatabase.addServerToDatabase(serverName)
        except Exception as databaseWritingError:
            print(f'Error occured while adding {serverName} server to the database...')
            print(databaseWritingError)

    def __getNotifyEmbed(self, animeInfo: dict):
        return discord.Embed(
            title=animeInfo['title'],
            description='You will get notified whenever a new episode launches!',
            colour=0x369e52,
        ).set_thumbnail(url=animeInfo['image_url'])

    def __getCurrentDayInJapan(self):
        return str(datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime("%A"))

    def __updateLatestEpisode(self, animeDb: dict):
        self.jsonDatabase.updateAnimeEntry(animeDb)

    def __removeFinishedAnime(self, serverName: str, animeTitle: str):
        self.jsonDatabase.deleteFromDatabase(serverName, animeTitle)

    def __notificationInfo(self, serverName: str, animeInfo: dict, episodeNumber: int):
        return {
            "server": serverName,
            "anime": animeInfo['title'],
            "episode": episodeNumber,
            "title": self.animeApi.getLatestEpisodeTitle(animeInfo['title'], episodeNumber),
            "finished": animeInfo['episodes'] == episodeNumber,
            "url": self.animeApi.getLatestEpisodeUrl(animeInfo['title'], episodeNumber)
        }

    ################ E M B E D   C O N F I G U R A T I O N ####################
    def __configureEmbed(self, animeInfo: dict):
        self.__setEmbedTitle(animeInfo['title'])
        self.__setEmbedDescription('Information')
        self.__setEmbedThumbnail(animeInfo['image_url'])
        self.__setEmbedUrl(animeInfo['url'])
        self.__setEmbedColour(0x3be2ff)
        self.__setEmbedTimestamp(datetime.datetime.now(pytz.timezone('Europe/Athens')))
        self.__setEmbedFooter(animeInfo['mal_image'], 'Data from MyAnimeList')
        self.__setEmbedInformationFields(animeInfo)

    def __setEmbedTitle(self, animeTitle: str):
        self.__discordEmbed.title = animeTitle

    def __setEmbedDescription(self, embedDescription: str):
        self.__discordEmbed.description = embedDescription

    def __setEmbedUrl(self, url: str):
        self.__discordEmbed.url = url
    
    def __setEmbedThumbnail(self, thumbnailUrl: str):
        self.__discordEmbed.set_thumbnail(url=thumbnailUrl)

    def __setEmbedColour(self, colour: int):
        self.__discordEmbed.colour = colour

    def __setEmbedFooter(self, iconUrl: str, text: str):
        self.__discordEmbed.set_footer(icon_url=iconUrl, text=text)

    def __setEmbedTimestamp(self, timestamp: datetime.datetime):
        self.__discordEmbed.timestamp = timestamp

    def __setEmbedInformationFields(self, animeInfo: dict):
        self.__discordEmbed.add_field(name='Type',      value=f'{animeInfo["type"]}',       inline=True)
        self.__discordEmbed.add_field(name='Source',    value=f'{animeInfo["source"]}',     inline=True)
        self.__discordEmbed.add_field(name='Studio',    value=f'{animeInfo["studio"]}',     inline=True)
        self.__discordEmbed.add_field(name='Episodes',  value=f'{animeInfo["episodes"]}',   inline=True)
        self.__discordEmbed.add_field(name='Score',     value=f'{animeInfo["score"]}',      inline=True)
        self.__discordEmbed.add_field(name='Rank',      value=f'#{animeInfo["rank"]}',      inline=True)
        self.__discordEmbed.add_field(name='Status',    value=f'{animeInfo["status"]}',     inline=True)
        self.__discordEmbed.add_field(name='Premiered', value=f'{animeInfo["premiered"]}',  inline=True)
        self.__discordEmbed.add_field(name='Broadcast', value=f'{animeInfo["broadcast"]}',  inline=True)
        self.__discordEmbed.add_field(name='Synopsis',  value=f'{animeInfo["synopsis"]}',   inline=False)

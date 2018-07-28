import os
import CrawlerBot

class Bot:
    def __init__(self, startAddress):
        self.__startAddress = startAddress
        self.__bot = CrawlerBot.Selenium()
        pass

    def bot_start(self):
        self.__bot.followExternalOnly(self.__startAddress)

startAddress = "https://www.google.co.kr"

Bot = Bot(startAddress)

Bot.bot_start()

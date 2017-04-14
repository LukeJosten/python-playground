#!/usr/bin/env python3
# amcEpisodeTracker.py - Tracks a particular episode on an amc show
# and sends out texts when the episode is available to stream!

from bs4 import BeautifulSoup
from twilio.rest import Client
import sys, requests, time, configparser

config = configparser.ConfigParser()
config.read('twilioConfig.ini')

TWILIO_ACCOUNT_SID = config.get('twilio', 'TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config.get('twilio', 'TWILIO_AUTH_TOKEN')
TWILIO_NUMBER_FROM = config.get('twilio', 'TWILIO_NUMBER_FROM')
TWILIO_NUMBERS_TO = config.get('twilio', 'TWILIO_NUMBERS_TO').split(',')

AMC_URL = "http://www.amc.com/shows/"

def main():
    if len(sys.argv) != 4:
        usage()
    
    try:
        showName = sys.argv[1]
        episodeNum = int(sys.argv[2])
        timeDelay = int(sys.argv[3])
    except ValueError:
        usage()
 
    showUrl = AMC_URL + showName

    pageContent = getWebPageContent(showUrl)
    isStreamable = isEpisodeAvailableToStream(pageContent, episodeNum)
    while (not isStreamable):
        print(showName + " ep " + str(episodeNum) + " is unavailable. Trying agin in " + str(timeDelay) + " seconds.")
        time.sleep(timeDelay)
        pageContent = getWebPageContent(showUrl)
        isStreamable = isEpisodeAvailableToStream(pageContent, episodeNum)

    successText = "Hurray! Episode " + str(episodeNum) + " of " + showName + " is now available to stream! " + showUrl
    print(successText)
    sendTexts(successText)
    sys.exit()

def getWebPageContent(url):
    webPage = requests.get(url)
    if (webPage.status_code != 200):
        print("Encountered an error while requesting: " + url)
        print("Status code: " + str(webPage.status_code))
        sys.exit()
    return webPage.content

def isEpisodeAvailableToStream(pageContent, episodeNum):
    soup = BeautifulSoup(pageContent, "html.parser")

    episodeListDiv = soup.findAll("div", "episode-list")
    episodeListLi = episodeListDiv[0].findAll("li")
    if (len(episodeListLi) < episodeNum):
        print("Error! The given episode could not be found")
        usage()
    streamableIconTag = episodeListLi[episodeNum - 1].findAll("span", "icon-video-play")

    return len(streamableIconTag) != 0

def sendTexts(message):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    for numberTo in TWILIO_NUMBERS_TO:
        client.messages.create(
            to = numberTo,
            from_ = TWILIO_NUMBER_FROM,
            body = message,
        )

def usage():
    print("Usage: amcEpisodeTracker.py [show name] [episode number] [time delay]")
    print("")
    print("show name: Must be separated with dashes (-) and is found on AMC's URL as amc.com/shows/<show-name>.")
    print("episode number: Must be a simple number and is the episode number of the most recent season.")
    print("time delay: Number of seconds to wait to check if the episode is available to stream again.")
    print("")
    print("Example: python amcEpisodeTracker.py better-call-saul 2 60")
    sys.exit()

if __name__ == "__main__":
    main()
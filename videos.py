from googleapiclient.discovery import build
import re
from config import YOUTUBE_API_KEY
from dbConnector import myCursor, myDB
import mysql.connector
import random
import logging


def searchTrailers(tvShowName, season, episode, typeOfSearch='notification'):
    """
    Searches YouTube for trailers related to a specific TV show, season, and episode.

    This function creates several search queries based on the TV show's name, season, and episode, and uses the YouTube Data API to retrieve relevant video details.
    It returns a list of YouTube video information about the trailers or notifications for the requested TV show.

    Args:
        tvShowName (str): The name of the TV show.
        season (int): The season number of the TV show.
        episode (int): The episode number of the TV show.
        typeOfSearch (str): The type of search to perform, either 'notification' or 'trailer'.

    Returns:
        list: A list of dictionaries containing details about the YouTube videos.

    Exceptions:
        Exception: If there is any error while querying the YouTube Data API or processing the response.
    """

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    queryStrings = [f'"{tvShowName}" "s{season:02d}e{episode:02d}"',
                    f'"{tvShowName}" "season {season}" "episode {episode}"',
                    f'"{tvShowName}" "{season}x{episode:02d}"']

    seenVideoIds = set()
    random.shuffle(queryStrings)

    order_by = "viewCount" if typeOfSearch == 'trailer' else "relevance"

    results=[]

    try:
        for queryString in queryStrings:
            request = youtube.search().list(
                q=queryString,
                part="snippet,id",
                type="video",
                videoDuration="short",
                maxResults=10,
                relevanceLanguage="en",
                order=order_by
            )
            response = request.execute()

            for videoItem in response.get('items', []):
                videoId = videoItem['id']['videoId']

                if videoId in seenVideoIds:
                    continue

                videoTitle = videoItem['snippet']['title']
                videoDescription = videoItem['snippet'].get('description', '').lower()

                if checkWrongShowOrSeason(videoTitle, videoDescription, tvShowName, season, episode):
                    continue

                videoData = {
                    "title": videoTitle,
                    "url": f"https://www.youtube.com/watch?v={videoId}",
                    "channel": videoItem['snippet']['channelTitle'],
                    "publishedAt": videoItem['snippet']['publishedAt'],
                    "description": videoDescription[:200] + "..." if len(videoDescription) > 200 else videoDescription
                }

                if not isVideoInDatabase(tvShowName, season, episode, videoData["url"]):
                    results.append(videoData)
                    seenVideoIds.add(videoId)

                if len(results) >= 2:
                    break

            if len(results) >= 2:
                break

        return results[:2]

    except Exception as error:
        logging.error(f"Error searching YouTube: {str(error)}")
        return []


def checkWrongShowOrSeason(videoTitle, videoDescription, showName, targetSeason, targetEpisode):
    """
    Validates if the video matches the correct TV show, season, and episode.

    This function checks the video title and description for patterns related to the show, season, and episode to confirm that the video matches the requested criteria.

    Args:
        videoTitle (str): The title of the YouTube video.
        videoDescription (str): The description of the YouTube video.
        showName (str): The name of the TV show.
        targetSeason (int): The season number of the TV show.
        targetEpisode (int): The episode number of the TV show.

    Returns:
        bool: True if the video is not relevant to the requested TV show, season, and episode, False otherwise.
    """
    titleLower = videoTitle.lower()
    descriptionLower = videoDescription.lower()
    showNameLower = showName.lower()

    if showNameLower not in titleLower:
        return True

    seasonPatterns = [r"season (\d+)", r"s(\d+)", r"(\d+)x", r"episode (\d+)", r"ep(\d+)"]

    foundSeason = None
    foundEpisode = None

    for seasonPattern in seasonPatterns:
        matches = re.findall(seasonPattern, titleLower)
        for match in matches:
            if isinstance(match, tuple):
                foundSeason = int(match[0])
                foundEpisode = int(match[1]) if len(match) > 1 else None
            else:
                foundSeason = int(match)

    if foundSeason is None and foundEpisode is None:
        matches = re.findall(r"season (\d+)", descriptionLower)
        if matches:
            foundSeason = int(matches[0])

    if foundSeason != targetSeason or (foundEpisode is not None and foundEpisode != targetEpisode):
        return True

    return False

def isVideoInDatabase(tvShowName, season, episode, videoUrl):
    """
    Checks whether a YouTube video already exists in the database for a particular TV show, season, and episode.

    This function queries the database to verify if a video URL for the specified show, season, and episode has already been stored.

    Args:
        tvShowName (str): The name of the TV show.
        season (int): The season number of the TV show.
        episode (int): The episode number of the TV show.
        videoUrl (str): The URL of the YouTube video.

    Returns:
        bool: True if the video is already in the database, False otherwise.

    Exceptions:
        mysql.connector.Error: If an error occurs while executing the query.
    """
    try:
        query = """
            SELECT tv_shows.id 
            FROM tv_shows 
            WHERE tv_shows.name = %s
        """
        myCursor.execute(query, (tvShowName,))
        result = myCursor.fetchone()

        if not result:
            logging.error(f"Error: Tv show '{tvShowName}' not found in the database")
            return False

        tv_show_id = result[0]

        query = """
            SELECT 1 
            FROM youtube_videos AS yv
            INNER JOIN tv_shows AS ts ON ts.id = yv.tv_show_id
            WHERE ts.id = %s AND yv.season = %s AND yv.episode = %s AND yv.url = %s
        """
        myCursor.execute(query, (tv_show_id, season, episode, videoUrl))
        result = myCursor.fetchone()

        return result is not None

    except mysql.connector.Error as error:
        logging.error(f"Error checking video in the database: {str(error)}")
        return False
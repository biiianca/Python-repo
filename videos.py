from googleapiclient.discovery import build
import re
from config import YOUTUBE_API_KEY

def searchTrailers(tvShowName, season, episode):

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    queryStrings = [f'"{tvShowName}" "s{season:02d}e{episode:02d}"',
                    f'"{tvShowName}" "season {season}" "episode {episode}"',
                    f'"{tvShowName}" "{season}x{episode:02d}"'
                    ]

    allVideos = []
    seenVideoIds = set()

    try:
        for queryString in queryStrings:
            request = youtube.search().list(q=queryString,
                                            part="snippet,id",
                                            type="video",
                                            videoDuration="short",
                                            maxResults=20,
                                            relevanceLanguage="en",
                                            order="relevance"
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

                videoData = {"title": videoTitle,
                            "url": f"https://www.youtube.com/watch?v={videoId}",
                            "channel": videoItem['snippet']['channelTitle'],
                            "publishedAt": videoItem['snippet']['publishedAt'],
                            "description": videoDescription[:200] + "..." if len(videoDescription) > 200 else videoDescription
                            }
                allVideos.append(videoData)
                seenVideoIds.add(videoId)

        return allVideos[:10]

    except Exception as error:
        print(f"Error searching YouTube: {str(error)}")
        return []


def checkWrongShowOrSeason(videoTitle, videoDescription, showName, targetSeason, targetEpisode):
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
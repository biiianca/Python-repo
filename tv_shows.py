import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
from dbConnector import myCursor, myDB
import mysql.connector
import requests
from datetime import datetime
from imdb import fetchNewShowsFromIMDB, getNextEpisode
from config import API_KEY
from videos import searchTrailers

def addTVshow(name, imdb_link, score):
    """
    This function inserts a new TV show into the 'tv_shows' table of the database.

    Args:
        name (str): The name of the TV show.
        imdb_link (str): The IMDb URL associated with the TV show.
        score (float): The rating assigned to the TV show.

    Exceptions:
        mysql.connector.Error: If an error occurs while executing the insert query.
    """
    try:
        query="INSERT INTO tv_shows (name, link, score) VALUES (%s, %s, %s)"
        myCursor.execute(query, (name, imdb_link, score))
        myDB.commit()
        logging.info(f"Tv show '{name}' added")
    except mysql.connector.Error as error:
        logging.error(f"Error at adding the tv show: {error}")


def addLastWatchedEpisode(episode, tv_show_name):
    """
        This function updates or sets the 'last_watched_episode' field for a specified TV show.

        Args:
            episode (str): The last episode watched, formatted as 'SxxExx'.
            tv_show_name (str): The name of the TV show.

        Exceptions:
            mysql.connector.Error: If an error occurs while executing the update query.
        """
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name=%s", (tv_show_name,))
        result=myCursor.fetchone()

        if result is None:
            logging.error(f"Error: '{tv_show_name}' not found in the database")
            return

        query="UPDATE tv_shows SET last_watched_episode=%s WHERE name=%s"
        myCursor.execute(query, (episode, tv_show_name))
        myDB.commit()
        logging.info(f"Episode '{episode}' updated for '{tv_show_name}'")
    except mysql.connector.Error as error:
        logging.error(f"Error updating the last watched episode: {error}")

def updateScore(score, tv_show_name):
    """
       This function modifies the rating score for a specific TV show.

       Args:
           score (float): The new score to be assigned to the TV show.
           tv_show_name (str): The name of the TV show.

       Exceptions:
           mysql.connector.Error: If an error occurs while executing the update query.
       """
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name=%s", (tv_show_name,))
        result=myCursor.fetchone()

        if result is None:
            logging.error(f"Error: '{tv_show_name}' not found in the database")
            return

        query = "UPDATE tv_shows SET score=%s WHERE name=%s"
        myCursor.execute(query, (score, tv_show_name))
        myDB.commit()
        logging.info(f"Score '{score}' was set for '{tv_show_name}'")

    except mysql.connector.Error as error:
        logging.error(f"Error updating the score: {error}")

def setDate(date, tv_show_name):
    """
       This function sets the last watched date for a TV show.

       Args:
           date (str): The date when the show was last watched, in 'YYYY-MM-DD' format.
           tv_show_name (str): The name of the TV show.

       Exceptions:
           mysql.connector.Error: If an error occurs while executing the update query.
       """
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name=%s", (tv_show_name,))
        result = myCursor.fetchone()

        if result is None:
            logging.info(f"Error: '{tv_show_name}' not found in the database")
            return

        query = "UPDATE tv_shows SET date=%s WHERE name=%s"
        myCursor.execute(query, (date, tv_show_name))
        myDB.commit()
        logging.info(f"Date '{date}' set for '{tv_show_name}'")

    except mysql.connector.Error as error:
        logging.error(f"Error updating the date: {error}")

def deleteTVShow(tv_show_name):
    """
        This function removes a TV show from the 'tv_shows' table.

        Args:
            tv_show_name (str): The name of the TV show to be removed.

        Exceptions:
            mysql.connector.Error: If an error occurs while executing the delete query.
        """
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name = %s", (tv_show_name,))
        result = myCursor.fetchone()

        if result is None:
            logging.error(f"TV Show '{tv_show_name}' not found in the database")
            return

        query = "DELETE FROM tv_shows WHERE name = %s"
        myCursor.execute(query, (tv_show_name,))
        myDB.commit()
        logging.info(f"TV Show '{tv_show_name}' deleted")

    except mysql.connector.Error as error:
        logging.error(f"Error at deleting the TV show: {error}")

def snoozeATVShow(tv_show_name):
    """
    This function marks a TV show as 'snoozed'.

    Args:
        tv_show_name (str): The name of the TV show to snooze.

    Exceptions:
        mysql.connector.Error: If an error occurs while executing the insert query.
    """
    try:
        query="SELECT id FROM tv_shows WHERE name = %s"
        myCursor.execute(query, (tv_show_name,))
        tv_show_id = myCursor.fetchone()

        if tv_show_id:
            tv_show_id = tv_show_id[0]

            try:
                secondQuery = "INSERT INTO snoozed_tv_shows (tv_show_id) VALUES (%s)"
                myCursor.execute(secondQuery, (tv_show_id,))
                myDB.commit()
                logging.info(f"TV Show '{tv_show_name}' has been snoozed")
            except mysql.connector.IntegrityError:
                logging.warning(f"TV Show '{tv_show_name}' is already snoozed")
        else:
            logging.error(f"No TV Show found with the name '{tv_show_name}' in the database")

    except mysql.connector.Error as error:
        logging.error(f"Error at snoozing the TV Show: {error}")


def unsnoozeATVShow(tv_show_name):
    """
    This function removes the snoozed TV show from the table 'snoozed_tv_shows'.

    Args:
        tv_show_name (str): The name of the TV show to unsnooze.

    Exceptions:
    mysql.connector.Error: If an error occurs while executing the delete query.
    """
    try:
        query = "SELECT id FROM tv_shows WHERE name = %s"
        myCursor.execute(query, (tv_show_name,))
        tv_show_id = myCursor.fetchone()

        if tv_show_id:
            tv_show_id = tv_show_id[0]

            test_query = "SELECT 'test' FROM snoozed_tv_shows WHERE tv_show_id = %s"
            myCursor.execute(test_query, (tv_show_id,))
            is_snoozed = myCursor.fetchone()

            if is_snoozed:
                secondQuery = "DELETE FROM snoozed_tv_shows WHERE tv_show_id = %s"
                myCursor.execute(secondQuery, (tv_show_id,))
                myDB.commit()
                logging.info(f"TV Show '{tv_show_name}' has been unsnoozed")
            else:
                logging.warning(f"TV Show '{tv_show_name}' isn't snoozed")
        else:
            logging.error(f"No TV Show found with the name '{tv_show_name}'")

    except mysql.connector.Error as error:
        logging.error(f"Error at unsnoozing the TV Show: {error}")

def listUnwatchedEpisodes():
    """
    This function lists the next episode (if exists) for all TV shows, excluding snoozed ones, ordered by rating.

    Exceptions:
    mysql.connector.Error: If an error occurs while executing the query.
    """
    try:
        query = """
            SELECT tv_shows.id, tv_shows.name, tv_shows.last_watched_episode, tv_shows.date, tv_shows.link, tv_shows.score
            FROM tv_shows
            WHERE tv_shows.id NOT IN (SELECT tv_show_id FROM snoozed_tv_shows)
            AND tv_shows.last_watched_episode IS NOT NULL
            ORDER BY tv_shows.score DESC;
        """
        myCursor.execute(query)
        results = myCursor.fetchall()

        if results:
            logging.info("New episodes for TV shows:\n")
            for row in results:
                tv_show_id, name, last_episode, date, link, score = row

                next_episode = getNextEpisode(link, last_episode)

                if next_episode:
                    next_episode_title = next_episode['title']
                    next_episode_season = next_episode['season']
                    next_episode_episode_number = next_episode['episode']
                else:
                    next_episode_title = " There are no more episodes for this TV Show! "
                    next_episode_season = next_episode_episode_number = None


                logging.info(f"Name: {name}")
                logging.info(f"Last Episode Watched: {last_episode}")
                logging.info(f"Last Watched Date: {date}")
                if next_episode_season is not None and next_episode_episode_number is not None:
                    logging.info(f"Next Episode: {next_episode_title} (S{next_episode_season}E{next_episode_episode_number})")
                else:
                    logging.info(f"----- {next_episode_title} ------")
                logging.info(f"IMDB Link: {link}")
                logging.info(f"Score: {score}")
                logging.info("-." * 30)
        else:
            logging.info("No new episodes available")

    except mysql.connector.Error as error:
        logging.error(f"Error at listing new episodes: {error}")


def getEarliestTVShowDate():
    """
    This function retrieves the release date of the earliest TV show in the database.

    This function gathers all TV show links from the database, retrieves the IMDb ID, and uses the OMDb API to fetch the release date.
    The function then returns the earliest release date in 'YYYY-MM-DD' format.
    If no TV shows are found or there's an error, it returns a default date of "2000-01-01".

    Returns:
        str: The earliest release date of TV shows in the database in 'YYYY-MM-DD' format, or "2000-01-01" if no data is available or an error occurs.

    Exceptions:
        mysql.connector.Error: If an error occurs while fetching data from the database.
        requests.exceptions.RequestException: If an error occurs during the request to the OMDb API.
    """
    try:
        myCursor.execute("SELECT link FROM tv_shows")
        results = myCursor.fetchall()

        if not results:
            logging.warning("No TV shows found in the database.")
            return "2000-01-01"

        release_dates = []

        for (link,) in results:
            imdb_id = link.split("/")[-2]
            url = f"https://www.omdbapi.com/?i={imdb_id}&apikey={API_KEY}"

            try:
                response = requests.get(url)
                data = response.json()

                if data.get("Response") == "True":
                    release_date = data.get("Released", "2000-01-01")
                    release_date = datetime.strptime(release_date, "%d %b %Y").strftime("%Y-%m-%d")
                    release_dates.append(release_date)
                else:
                    logging.error(f"Error fetching data for {link}: {data.get('Error')}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Request error for {link}: {e}")

        if release_dates:
            return min(release_dates)
        else:
            return "2000-01-01"

    except mysql.connector.Error as error:
        logging.error(f"Error retrieving show links: {error}")
        return "2000-01-01"


def getAverageScore():
    """
    This function computes the average score of all TV shows in the database.

    If no score is found or there are no TV shows it returns a default score of 5.

    In case of an error during the query, it logs the error and returns 0.

    Returns:
        float: The average score of all TV shows, or 5 if no score exists, or 0 if an error occurs.

    Exceptions:
        mysql.connector.Error: If an error occurs while executing the query.
    """
    try:
        myCursor.execute("SELECT AVG(score) FROM tv_shows")
        result = myCursor.fetchone()
        return result[0] if result[0] else 5
    except mysql.connector.Error as error:
        logging.error(f"Error calculating average score: {error}")
        return 0


def showNewTVShows():
    """
    This function displays new TV shows for the user based on the earliest release date and average score.

    Then retrieves new TV shows from IMDB based on those criteria.

    The earliest date, average score, and recommended shows are logged and if no shows meet the criteria, it logs that no shows were found.

    Logs:
        - Earliest release date from the database.
        - Average score from the database.
        - Recommended TV shows with their title, score, release date, and link.

    """
    latest_date = getEarliestTVShowDate()
    average_score = getAverageScore()
    new_shows = fetchNewShowsFromIMDB(latest_date, average_score)

    logging.info(f"Earliest TV Show release date in the database: {latest_date}")
    logging.info(f"Average score in the database: {average_score:.2f}")

    logging.info("TV Shows recommended:")
    if new_shows:
        for show in new_shows:
            logging.info(
                f"- {show['title']} (Score: {show['score']:.1f}, Release Date: {show['release_date']}, Link: {show['link']})")
    else:
        logging.info("Couldn't find TV Shows!")


def addVideos(tv_show_id, season, episode, videos, tv_show_name, type_of_search):
    """
    This function inserts video URLs for a specific TV show, season, and episode in the 'youtube_videos' table.

    If the search type is 'notification', it logs a notification message about the saved videos.

    If a database error occurs, it logs the error.

    Args:
        tv_show_id (int): The ID of the TV show.
        season (int): The season number.
        episode (int): The episode number.
        videos (list): A list of dictionaries containing video URLs and metadata.
        tv_show_name (str): The name of the TV show.
        type_of_search (str): The type of search ('notification' or 'trailer').

    Exceptions:
        mysql.connector.Error: If an error occurs while executing the insert query.
    """
    try:
        query = """
                INSERT INTO youtube_videos (tv_show_id, season, episode, url, type)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE url = VALUES(url), type = VALUES(type);
            """
        myCursor.executemany(query, [
            (tv_show_id, season, episode, video["url"], type_of_search) for video in videos
        ])
        myDB.commit()

        if type_of_search == 'notification':
            logging.info(f"Saved new videos for '{tv_show_name}', Season {season}, Episode {episode}")
        else:
            logging.info(f"Saved new videos for '{tv_show_name}', Season {season}, Episode {episode}")

    except mysql.connector.Error as error:
        logging.error(f"Error saving videos to database: {error}")


def listNewVideos(tv_show_name, season, episode, type_of_search):
    """
    This function searches for videos (that were not requested before) related to a TV show, season, and episode.

    If videos are found, they are logged, and then added to the database.

    If no videos are found, it logs that no videos were found.

    Args:
        tv_show_name (str): The name of the TV show.
        season (int): The season number.
        episode (int): The episode number.
        type_of_search (str): The type of search ('notification' or 'trailer').
    """
    try:
        query = "SELECT id FROM tv_shows WHERE name = %s"
        myCursor.execute(query, (tv_show_name,))
        tv_show_id = myCursor.fetchone()

        if not tv_show_id:
            logging.error(f"TV Show '{tv_show_name}' not found")
            return

        tv_show_id = tv_show_id[0]

        videos = searchTrailers(tv_show_name, season, episode, 'trailer')

        if videos:
            logging.info("New videos found:")
            for video in videos:
                logging.info(f"- {video['title']} ({video['publishedAt']})\n  {video['url']}")

            addVideos(tv_show_id, season, episode, videos, tv_show_name, type_of_search)
        else:
            logging.info("No videos found for this episode")
    except Exception as error:
        logging.error(f"Error in listNewVideos: {str(error)}")

def notifyForNewVideos(type_of_search):
    """
    This function notifies the user when new videos are found for TV shows with existing videos in the database.

    If new videos are found, they are added to the database, and a notification is logged.
    If no new videos are found, a message indicating that no new videos were found is logged.

    Args:
        type_of_search (str): The type of search ('notification').
    """
    try:
        query = """
            SELECT DISTINCT tv_shows.id, tv_shows.name, youtube_videos.season, youtube_videos.episode
            FROM tv_shows
            JOIN youtube_videos ON tv_shows.id = youtube_videos.tv_show_id
        """
        myCursor.execute(query)
        tv_shows = myCursor.fetchall()

        if not tv_shows:
            logging.info("No TV shows found with existing videos in youtube_videos.")
            return

        for tv_show in tv_shows:
            tv_show_id, tv_show_name, season, episode = tv_show

            videos = searchTrailers(tv_show_name, season, episode)

            if videos:
                logging.info(f"New videos found for {tv_show_name} (S{season}E{episode})!")
                addVideos(tv_show_id, season, episode, videos, tv_show_name, type_of_search)
            else:
                logging.info(f"No videos found for {tv_show_name}")
    except Exception as error:
        logging.error(f"Error in notifyForNewVideos (search for existing TV shows in youtube_videos): {str(error)}")


def markVideosAsSeen():
    """
    This function marks all videos of type 'notification' as 'seen' in the database when the user requests to see the notifications.

    A confirmation message is logged after the update is complete.

    Exceptions:
        mysql.connector.Error: If an error occurs while executing the query.
    """
    try:
        query = """
            UPDATE youtube_videos
            SET type = 'seen'
            WHERE type = 'notification'
        """
        myCursor.execute(query, )
        myDB.commit()
        logging.info(f"You're up to date with the videos!")
    except mysql.connector.Error as error:
        logging.error(f"Error marking videos as seen: {error}")


def see_notifications():
    """
    This function retrieves and displays the TV Shows that were found to have new video uploads.

    This function queries the database for TV shows with new videos marked as 'notification', excluding shows in the 'snoozed_tv_shows' list.

    It returns a message containing the names, seasons, episodes, and URLs of the new videos.

    If no new videos are available, a message indicating that is returned.

    Returns:
        str: A message listing new videos or indicating no new videos are available.

    Exception:
        mysql.connector.Error: If an error occurs while executing the query.
    """
    try:
        query = """
            SELECT tv_shows.name, youtube_videos.season, youtube_videos.episode, youtube_videos.url
            FROM youtube_videos
            JOIN tv_shows ON youtube_videos.tv_show_id = tv_shows.id
            WHERE youtube_videos.type = 'notification'
            AND tv_shows.id NOT IN (SELECT tv_show_id FROM snoozed_tv_shows)
        """
        myCursor.execute(query)
        results = myCursor.fetchall()

        if results:
            message = "New videos to watch:"
            for row in results:
                show_name, season, episode, url = row
                message += f"\nTV Show: {show_name} - S{season}E{episode} - {url}"
            return message
        else:
            return "No new videos available!"
    except mysql.connector.Error as error:
        return f"Error retrieving notifications: {error}"
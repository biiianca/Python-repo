from dbConnector import myCursor, myDB
import mysql.connector
import requests
from datetime import datetime
from imdb import fetchNewShowsFromIMDB, getNextEpisode
from config import API_KEY
from videos import searchTrailers

def addTVshow(name, imdb_link, score):
    try:
        query="INSERT INTO tv_shows (name, link, score) VALUES (%s, %s, %s)"
        myCursor.execute(query, (name, imdb_link, score))
        myDB.commit()
        print(f"Tv show '{name}' added")
    except mysql.connector.Error as error:
        print(f"Error at adding the tv show: {error}")


def addLastWatchedEpisode(episode, tv_show_name):
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name=%s", (tv_show_name,))
        result=myCursor.fetchone()

        if result is None:
            print(f"Error: '{tv_show_name}' not found in the database")
            return

        query="UPDATE tv_shows SET last_watched_episode=%s WHERE name=%s"
        myCursor.execute(query, (episode, tv_show_name))
        myDB.commit()
        print(f"Episode '{episode}' updated for '{tv_show_name}'")
    except mysql.connector.Error as error:
        print(f"Error updating the last watched episode: {error}")

def updateScore(score, tv_show_name):
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name=%s", (tv_show_name,))
        result=myCursor.fetchone()

        if result is None:
            print(f"Error: '{tv_show_name}' not found in the database")
            return

        query = "UPDATE tv_shows SET score=%s WHERE name=%s"
        myCursor.execute(query, (score, tv_show_name))
        myDB.commit()
        print(f"Score '{score}' was set for '{tv_show_name}'")

    except mysql.connector.Error as error:
        print(f"Error updating the score: {error}")

def setDate(date, tv_show_name):
    try:
        myCursor.execute("SELECT * FROM tv_shows WHERE name=%s", (tv_show_name,))
        result = myCursor.fetchone()

        if result is None:
            print(f"Error: '{tv_show_name}' not found in the database")
            return

        query = "UPDATE tv_shows SET date=%s WHERE name=%s"
        myCursor.execute(query, (date, tv_show_name))
        myDB.commit()
        print(f"Date '{date}' set for '{tv_show_name}'")

    except mysql.connector.Error as error:
        print(f"Error updating the date: {error}")

def deleteTVShow(tv_show_name):
    try:
        query="DELETE FROM tv_shows WHERE name = %s"
        myCursor.execute(query, (tv_show_name,))
        myDB.commit()
        print(f"Tv show '{tv_show_name}' deleted")
    except mysql.connector.Error as error:
        print(f"Error at deleting the tv show: {error}")

def snoozeATVShow(tv_show_name):
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
                print(f"TV Show '{tv_show_name}' has been snoozed")
            except mysql.connector.IntegrityError:
                print(f"TV Show '{tv_show_name}' is already snoozed")
        else:
            print(f"No TV Show found with the name '{tv_show_name}' in the database")

    except mysql.connector.Error as error:
        print(f"Error at snoozing the TV Show: {error}")


def unsnoozeATVShow(tv_show_name):
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
                print(f"TV Show '{tv_show_name}' has been unsnoozed")
            else:
                print(f"TV Show '{tv_show_name}' isn't snoozed")
        else:
            print(f"No TV Show found with the name '{tv_show_name}'")

    except mysql.connector.Error as error:
        print(f"Error at unsnoozing the TV Show: {error}")

def listUnwatchedEpisodes():
    try:
        query =  """
                SELECT tv_shows.id, tv_shows.name, tv_shows.last_watched_episode, tv_shows.date, tv_shows.link, tv_shows.score
                FROM tv_shows
                WHERE tv_shows.id NOT IN (SELECT tv_show_id FROM snoozed_tv_shows)
                ORDER BY tv_shows.score DESC;
                """
        myCursor.execute(query)
        results = myCursor.fetchall()

        if results:
            print("New episodes for TV shows:\n")
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


                print(f"Name: {name}")
                print(f"Last Episode Watched: {last_episode}")
                print(f"Last Watched Date: {date}")
                if next_episode_season is not None and next_episode_episode_number is not None:
                    print(f"Next Episode: {next_episode_title} (S{next_episode_season}E{next_episode_episode_number})")
                else:
                    print("-----", next_episode_title, "------")
                print(f"IMDB Link: {link}")
                print(f"Score: {score}")
                print("-." * 30)
        else:
            print("No new episodes available")

    except mysql.connector.Error as error:
        print(f"Error at listing new episodes: {error}")


def getNewestTVShowDate():
    try:
        myCursor.execute("SELECT link FROM tv_shows")
        results = myCursor.fetchall()

        if not results:
            print("No TV shows found in the database.")
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
                    print(f"Error fetching data for {link}: {data.get('Error')}")
            except requests.exceptions.RequestException as e:
                print(f"Request error for {link}: {e}")

        if release_dates:
            return max(release_dates)
        else:
            return "2000-01-01"

    except mysql.connector.Error as error:
        print(f"Error retrieving show links: {error}")
        return "2000-01-01"


def getAverageScore():
    try:
        myCursor.execute("SELECT AVG(score) FROM tv_shows")
        result = myCursor.fetchone()
        return result[0] if result[0] else 5
    except mysql.connector.Error as error:
        print(f"Error calculating average score: {error}")
        return 0


def showNewTVShows():
    latest_date = getNewestTVShowDate()
    average_score = getAverageScore()
    new_shows = fetchNewShowsFromIMDB(latest_date, average_score)

    print(f"Newest TV Show in the database has the date: {latest_date}")
    print(f"Average score in the database: {average_score:.2f}")

    print("\nNew TV Shows recommended:")
    if new_shows:
        for show in new_shows:
            print(
                f"- {show['title']} (Score: {show['score']:.1f}, Release Date: {show['release_date']}, Link: {show['link']})")
    else:
        print("Couldn't find TV Shows.")


def addVideos(tv_show_id, season, episode, videos, tv_show_name):
    try:
        query = """
                INSERT INTO youtube_videos (tv_show_id, season, episode, url)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE url = VALUES(url);
            """
        myCursor.executemany(query, [
            (tv_show_id, season, episode, video["url"]) for video in videos
        ])
        myDB.commit()
        print(f"Saved videos for TV Show '{tv_show_name}', Season {season}, Episode {episode}")
    except mysql.connector.Error as error:
        print(f"Error saving videos to database: {error}")


def getNewVideos(tv_show_id, season, episode, videos):
    new_videos = []
    try:
        query = """
                SELECT url FROM youtube_videos WHERE tv_show_id = %s AND season = %s AND episode = %s
            """
        myCursor.execute(query, (tv_show_id, season, episode))
        existing_urls = {row[0] for row in myCursor.fetchall()}

        for video in videos:
            if video["url"] not in existing_urls:
                new_videos.append(video)

    except mysql.connector.Error as error:
        print(f"Error checking for new videos: {error}")
    return new_videos

def listNewVideos(tv_show_name, season, episode):
    try:
        query = "SELECT id FROM tv_shows WHERE name = %s"
        myCursor.execute(query, (tv_show_name,))
        tv_show_id = myCursor.fetchone()

        if not tv_show_id:
            print(f"TV Show '{tv_show_name}' not found")
            return

        tv_show_id = tv_show_id[0]

        videos = searchTrailers(tv_show_name, season, episode)

        if videos:
            new_videos = getNewVideos(tv_show_id, season, episode, videos)

            if new_videos:
                print("New videos found:")
                for video in new_videos:
                    print(f"- {video['title']} ({video['publishedAt']})\n  {video['url']}")

                addVideos(tv_show_id, season, episode, new_videos, tv_show_name)
            else:
                print("No more new uploads found")
        else:
            print("No videos found for this episode")
    except Exception as error:
        print(f"Error in listNewVideos: {str(error)}")
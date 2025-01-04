from dbConnector import myCursor, myDB
import mysql.connector
import requests
from datetime import datetime
from imdb import fetchNewShowsFromIMDB
from config import API_KEY

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



def getWatchedTVShows():
    try:
        myCursor.execute("SELECT name, link, last_watched_episode FROM tv_shows WHERE score>=7")
        return myCursor.fetchall()
    except mysql.connector.Error as error:
        print(f"Error fetching unwatched TV shows: {error}")
        return []


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

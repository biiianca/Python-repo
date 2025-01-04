from dbConnector import myCursor, myDB
import mysql.connector

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

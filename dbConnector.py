import logging

import mysql.connector

myDB=mysql.connector.connect(host="localhost", user="root", password="stud", database="bingewatch")

myCursor=myDB.cursor()

def createTable():
    """
    This function creates the 'tv_shows' table

    The 'tv_shows' table contains the following columns:
    - id: An auto-incremented primary key.
    - name: A unique, non-null string representing the TV show's name.
    - link: A unique, non-null string representing the URL of the TV show's IMDb page.
    - score: A float between 1.0 and 10.0 representing the TV show's rating.
    - last_watched_episode: A string representing the last watched episode in the format 'SxxExx'.
    - date: A date field indicating the last time the TV show was watched.
    It ensures that:
    - The name and link are unique and not null.
    - The score is between 1.0 and 10.0.
    - The 'last_watched_episode' is a varchar with a maximum length of 50 characters.
    - The 'date' is a date format.

    Logs whether the operation of creating the table is successful or not.

    Raises:
        mysql.connector.Error: If an error occurs while executing the SQL query to create the table.
    """
    try:
        myCursor.execute("CREATE TABLE tv_shows (id INT AUTO_INCREMENT PRIMARY KEY, "
                                                "name VARCHAR(255) UNIQUE NOT NULL,"
                                                "link VARCHAR(255) UNIQUE NOT NULL,"
                                                "score FLOAT NOT NULL CHECK(score>=1.0 AND score<=10.0),"
                                                "last_watched_episode VARCHAR(50),"
                                                "date DATE)")
        logging.info("tv_shows table created")
    except mysql.connector.Error as error:
        logging.error(f"Error at creating the table <tv_shows>: {error}")


def addTVShows():
    """
    This function adds a list of TV shows to the 'tv_shows' table.

    Logs success or failure during the insertion process.

    Raises:
        mysql.connector.Error: If an error occurs while executing the insert query.
    """
    tv_shows = [
        ("Band of Brothers", "https://www.imdb.com/title/tt0185906/", 8.4, "S01E08"),
        ("Game of Thrones", "https://www.imdb.com/title/tt0944947/", 4.2, "S07E05"),
        ("The Sopranos", "https://www.imdb.com/title/tt0141842/", 7.2, "S01E13"),
        ("Sherlock", "https://www.imdb.com/title/tt1475582/", 5.1, "S03E03"),
        ("The Wire", "https://www.imdb.com/title/tt0306414/", 6.3, "S02E10"),
        ("Stranger Things", "https://www.imdb.com/title/tt4574334/", 8.7, "S05E05"),
        ("The Mandalorian", "https://www.imdb.com/title/tt8111088/", 8.7, "S01E04"),
        ("Dark", "https://www.imdb.com/title/tt5753856/", 6.8, "S03E08"),
        ("Friends", "https://www.imdb.com/title/tt0108778/", 8.9, "S01E18"),
        ("The Office", "https://www.imdb.com/title/tt0386676/", 9.0, "S09E24"),
        ("Parks and Recreation", "https://www.imdb.com/title/tt1266020/", 3.6, "S01E01"),
        ("The Crown", "https://www.imdb.com/title/tt4786824/", 4.7, "S02E03"),
        ("The Boys", "https://www.imdb.com/title/tt1190634/", 8.7, "S04E06"),
        ("Squid Game", "https://www.imdb.com/title/tt10919420/", 9.56, "S02E01"),
        ("Wednesday", "https://www.imdb.com/title/tt13443470/", 7.6, "S01E03"),
        ("You", "https://www.imdb.com/title/tt7335184/", 8.3,"S04E10"),
        ("The Rookie", "https://www.imdb.com/title/tt7587890/", 5.7, "S02E04")
    ]

    try:
        query = "INSERT INTO tv_shows (name, link, score, last_watched_episode) VALUES (%s, %s, %s, %s)"
        myCursor.executemany(query, tv_shows)
        myDB.commit()
    except mysql.connector.Error as error:
        logging.error(f"Error adding the TV shows: {error}")


def createTableForSnoozedTVShows():
    """
    This function creates the 'snoozed_tv_shows' table in the database.

    The table contains an auto-incrementing id for each snoozed TV show, along with a foreign key that links to the 'tv_shows' table.
    Logs whether the table creation is successful or encounters an error.

    Raises:
        mysql.connector.Error: If an error occurs while executing the query.

    """
    try:
        myCursor.execute("""
            CREATE TABLE snoozed_tv_shows (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tv_show_id INT UNIQUE,
                FOREIGN KEY (tv_show_id) REFERENCES tv_shows(id) ON DELETE CASCADE
            )
        """)
        logging.info("snoozed_tv_shows table created")
    except mysql.connector.Error as error:
        logging.error(f"Error at creating the table <snoozed_tv_shows>: {error}")


def createTableForVideos():
    """
    This function creates the 'youtube_videos' table that contains columns such as:
    - id: An auto-incremented primary key.
    - tv_show_id: The associated TV show id (foreign key linking to 'tv_shows')
    - season
    - episode
    - url
    - type: Indicates whether the video was added based on a user's request for uploads for a specific TV show or inserted by the notification system

    The function logs whether the table creation is successful or if an error occurs.

    Raises:
        mysql.connector.Error: If there is an error during query execution.
    """
    try:
        myCursor.execute("""
            CREATE TABLE youtube_videos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tv_show_id INT NOT NULL,
                season INT,
                episode INT,
                url VARCHAR(255) UNIQUE,
                type VARCHAR(20),
                FOREIGN KEY (tv_show_id) REFERENCES tv_shows(id) ON DELETE CASCADE
            )
        """)
        logging.info("youtube_videos table created")
    except mysql.connector.Error as error:
        logging.error(f"Error at creating the table <youtube_videos>: {error}")

def getAllTVShowsInTheDB():
    """
    This function executes a query to retrieve all TV show names stored in the table 'tv_shows' and returns them as a list of strings.

    Returns:
        list: A list containing the names of all TV shows.

    Raises:
        mysql.connector.Error: If an error occurs while executing the query.
    """
    try:
        query = "SELECT name FROM tv_shows"
        myCursor.execute(query)

        result = myCursor.fetchall()

        tv_show_names = [row[0] for row in result]
        return tv_show_names

    except mysql.connector.Error as error:
        logging.error(f"Error fetching TV show names: {error}")
        return []

def checkIfTableExists(table_name):
    """
    This function executes a query to check if a certain table exists in the database.

    Args:
        table_name (str): The name of the table

    Returns:
        bool: True if the table exists, False otherwise

    Raises:
        mysql.connector.Error: If an error occurs while executing the query.
    """
    query = f"SHOW TABLES LIKE '{table_name}'"
    myCursor.execute(query)
    result = myCursor.fetchone()
    return result is not None

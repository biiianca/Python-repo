import mysql.connector

myDB=mysql.connector.connect(host="localhost", user="root", password="stud", database="bingewatch")

myCursor=myDB.cursor()

def createTable():
    try:
        myCursor.execute("CREATE TABLE tv_shows (id INT AUTO_INCREMENT PRIMARY KEY, "
                                                "name VARCHAR(255) UNIQUE NOT NULL,"
                                                "link VARCHAR(255) UNIQUE NOT NULL,"
                                                "score FLOAT NOT NULL CHECK(score>=1.0 AND score<=10.0),"
                                                "last_watched_episode VARCHAR(50),"
                                                "date DATE)")
        print("tv_shows tabel created")
    except mysql.connector.Error as error:
        print(f"Error at creating the table <tv_shows>: {error}")


def addTVShows():
    tv_shows = [
        ("Band of Brothers", "https://www.imdb.com/title/tt0185906/", 8.4, "S1E8"),
        ("Game of Thrones", "https://www.imdb.com/title/tt0944947/", 4.2, "S8E6"),
        ("The Sopranos", "https://www.imdb.com/title/tt0141842/", 7.2, "S6E21"),
        ("Sherlock", "https://www.imdb.com/title/tt1475582/", 5.1, "S4E3"),
        ("The Wire", "https://www.imdb.com/title/tt0306414/", 6.3, "S5E10"),
        ("Stranger Things", "https://www.imdb.com/title/tt4574334/", 8.7, "S4E9"),
        ("The Mandalorian", "https://www.imdb.com/title/tt8111088/", 8.7, "S3E8"),
        ("Dark", "https://www.imdb.com/title/tt5753856/", 6.8, "S3E8"),
        ("Friends", "https://www.imdb.com/title/tt0108778/", 8.9, "S10E17"),
        ("The Office", "https://www.imdb.com/title/tt0386676/", 9.0, "S9E27"),
        ("Parks and Recreation", "https://www.imdb.com/title/tt1266020/", 3.6, "S7E13"),
        ("The Crown", "https://www.imdb.com/title/tt4786824/", 4.7, "S5E10"),
        ("The Boys", "https://www.imdb.com/title/tt1190634/", 8.7, "S3E8"),
    ]

    try:
        query = "INSERT INTO tv_shows (name, link, score, last_watched_episode) VALUES (%s, %s, %s, %s)"
        myCursor.executemany(query, tv_shows)
        myDB.commit()
    except mysql.connector.Error as error:
        print(f"Error adding the TV shows: {error}")


def createTableForSnoozedTVShows():
    try:
        myCursor.execute("CREATE TABLE snoozed_tv_shows (id INT AUTO_INCREMENT PRIMARY KEY, "
                                                "tv_show_id INT,"
                                                "FOREIGN KEY (tv_show_id) REFERENCES tv_shows(id) ON DELETE CASCADE")
        print("snoozed_tv_shows tabel created")
    except mysql.connector.Error as error:
        print(f"Error at creating the table <snoozed_tv_shows>: {error}")
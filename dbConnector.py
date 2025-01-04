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
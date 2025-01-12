import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
import threading
from tv_shows import showNewTVShows, addTVshow, addLastWatchedEpisode, updateScore, setDate, listUnwatchedEpisodes, \
    snoozeATVShow, unsnoozeATVShow, listNewVideos, see_notifications, \
    markVideosAsSeen, notifyForNewVideos
from imdb import getNameFromLink
from utils import verifyEpisodeFormat, verifyDateFormat
from dbConnector import createTable, addTVShows, createTableForSnoozedTVShows, createTableForVideos, checkIfTableExists, getAllTVShowsInTheDB

logging.basicConfig(filename='notifications.log', level=logging.INFO, format='%(asctime)s - %(message)s')


def notify_for_new_videos():
    try:
        notifyForNewVideos("notification")
        logging.info("Notification check completed.")
    except Exception as e:
        logging.error(f"Error in notifyForNewVideos: {e}")

    threading.Timer(60, notify_for_new_videos).start()


def start_notification_thread():
    notification_thread = threading.Thread(target=notify_for_new_videos, daemon=True)
    notification_thread.start()


def main():
    try:
        if not checkIfTableExists('tv_shows'):
            createTable()
        if not checkIfTableExists('snoozed_tv_shows'):
            createTableForSnoozedTVShows()
        if not checkIfTableExists('youtube_videos'):
            createTableForVideos()
    except Exception as e:
        print(f"Error creating tables: {e}")

    start_notification_thread()

    while True:
        try:
            cmd = input("-> ").strip()
            if cmd.lower() == "exit":
                break

            args = cmd.split()

            if args[0] == "add" and len(args) == 3:
                imdb_link = args[1]
                score = float(args[2])
                tv_show_name = getNameFromLink(imdb_link)
                print(tv_show_name)
                addTVshow(tv_show_name, imdb_link, score)

            elif " ".join(args[:3]).lower() == "print tv shows":
                tv_shows = getAllTVShowsInTheDB()
                for index, tv_show in enumerate(tv_shows, start=1):
                    print(f"{index}. {tv_show}")

            elif " ".join(args[:2]).lower() == "see notifications":
                print(see_notifications())
                markVideosAsSeen()

            elif args[:2] == ["update", "episode"] and len(args) >= 4:
                last_watched_episode = args[-1]
                tv_show_name = " ".join(args[2:-1])
                if verifyEpisodeFormat(last_watched_episode):
                    addLastWatchedEpisode(last_watched_episode, tv_show_name)
                else:
                    print("Error: Invalid episode format! Usage: update episode <TV Show Name> S<season>E<episode>")

            elif args[:2] == ["update", "score"] and len(args) >= 4:
                tv_show_name = " ".join(args[3:])
                score = args[2]
                updateScore(score, tv_show_name)

            elif args[:2] == ["set", "date"] and len(args) >= 4:
                tv_show_name = " ".join(args[3:])
                date = args[2]
                if not verifyDateFormat(date):
                    print("Error: invalid date format. Usage: year-month-day (dd-mm-yyyy)!")
                    continue
                setDate(date, tv_show_name)

            elif args[0] == "snooze" and len(args) >= 2:
                tv_show_name = " ".join(args[1:])
                snoozeATVShow(tv_show_name)

            elif args[0] == "unsnooze" and len(args) >= 2:
                tv_show_name = " ".join(args[1:])
                unsnoozeATVShow(tv_show_name)

            elif args[:2] == ['list', 'trailers'] and len(args) >= 5:
                try:
                    command_str = " ".join(args[2:])
                    if 'Season:' in command_str and 'Episode:' in command_str:
                        tv_show_name = command_str.split('Season:')[0].strip()
                        season_str = command_str.split('Season:')[1].split('Episode:')[0].strip()
                        episode_str = command_str.split('Episode:')[1].strip()
                        season = int(season_str)
                        episode = int(episode_str)
                        listNewVideos(tv_show_name, season, episode, "trailer")
                    else:
                        print("Error: Invalid command! Usage: list trailers <TV Show Name> Season:<Number> Episode:<Number>")

                except (ValueError, IndexError) as e:
                    print(f"Error: {e}")

            else:
                print("Invalid command")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

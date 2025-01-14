import logging
from datetime import datetime
import requests
from config import API_KEY

def getNameFromLink(imdb_link):
    """
    Retrieves the title of a TV show from an IMDb link using the OMDB API.

    This function extracts the IMDb ID from the provided IMDb link and then uses the OMDB API to retrieve the corresponding title of the TV show.
    If successful, it returns the title, otherwise it returns 'None'.

    Args:
        imdb_link (str): The IMDb URL of the TV show or movie.

    Returns:
        str: The title of the TV show or movie, or 'None' if there was an error during the request.

    Exceptions:
        Exception: If there is an issue with fetching data from the OMDB API.
    """
    imdbID = imdb_link.split("/")[-2]
    url = f"https://www.omdbapi.com/?i={imdbID}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get('Response') == 'True':
            return data.get('Title')
        else:
            raise Exception(f"Error fetching data: {data.get('Error')}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")
        return None

def getNextEpisode(link, last_episode_watched):
    """
    Retrieves the next episode's details for a given TV show using its IMDb link.

    Using the TVMaze API, this function finds the next episode of a TV show based on the last episode watched.
    The IMDb link identifies the show, and the last episode watched helps determine which episode to fetch.

    Args:
        link (str): IMDb URL for the TV show.
        last_episode_watched (str): The last episode watched, in the format "SxxExx" (e.g., "S01E05").

    Returns:
        dict: A dictionary with details of the next episode, such as the title, season, and episode number, or 'None' if the next episode is not found.

    Exceptions:
        requests.exceptions.RequestException: If there is an error during the HTTP request.
    """
    imdbID = link.split("/")[-2]
    url = f"http://api.tvmaze.com/lookup/shows?imdb={imdbID}"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200 and data:
            tv_show_id = data.get('id')
            if tv_show_id:
                episodes_url = f"http://api.tvmaze.com/shows/{tv_show_id}/episodes"
                episodes_response = requests.get(episodes_url)
                episode_list = episodes_response.json()

                season_number, episode_number = map(int, last_episode_watched[1:].split('E'))
                next_episode_details = None

                for episode in episode_list:
                    episode_season = episode['season']
                    episode_episode_number = episode['number']
                    if episode_season == season_number and episode_episode_number == episode_number + 1:
                        next_episode_details = episode
                        break
                    elif episode_season == season_number + 1 and episode_episode_number == 1:
                        next_episode_details = episode
                        break

                if next_episode_details:
                    next_episode_info = {
                        'title': next_episode_details['name'],
                        'season': next_episode_details['season'],
                        'episode': next_episode_details['number'],
                        'imdbID': imdbID
                    }
                    return next_episode_info
                else:
                    return None

            else:
                logging.error(f"Error: Couldn't find TV Show id for {imdbID}")
                return None

        else:
            logging.error(f"Error fetching data for {imdbID}: {data.get('Error', 'Unknown Error')}")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


def fetchNewShowsFromIMDB(min_date, min_score):
    """
    Fetches a list of new TV shows from IMDb, filtered by release date and IMDb rating.

    This function queries the OMDB API for new TV shows and filters the results based on the specified minimum release date and IMDb score.
    The results are sorted by release date.

    Args:
        min_date (str): The earliest release date for the TV shows, formatted as "YYYY-MM-DD".
        min_score (float): The minimum IMDb rating required for the shows.

    Returns:
        list: A list of dictionaries, each containing the title, release date, IMDb rating, and IMDb link for the new shows.

    Exceptions:
        requests.exceptions.RequestException: If there is an issue making requests to the OMDB API.
    """
    new_shows = []
    page = 1

    try:
        while len(new_shows) < 15:
            url = f"https://www.omdbapi.com/?apikey={API_KEY}&s=series&type=series&page={page}"
            response = requests.get(url)
            data = response.json()
            #logging.info(data)

            if data.get("Response") == "True":
                for item in data.get("Search", []):
                    imdb_id = item.get("imdbID")
                    try:
                        show_details = requests.get(f"https://www.omdbapi.com/?apikey={API_KEY}&i={imdb_id}").json()
                        release_date_raw = show_details.get("Released", "2000-01-01")
                        if release_date_raw == "N/A":
                            release_date = "2000-01-01"
                        else:
                            release_date = datetime.strptime(release_date_raw, "%d %b %Y").strftime("%Y-%m-%d")

                        score_str = show_details.get("imdbRating", "0")
                        if score_str == "N/A":
                            score = 0.0
                        else:
                            score = float(score_str)

                        if release_date > min_date and score > min_score:
                            new_shows.append({
                                "title": show_details.get("Title"),
                                "score": score,
                                "release_date": release_date,
                                "link": f"https://www.imdb.com/title/{imdb_id}/"
                            })
                    except Exception as e:
                        logging.error(f"Error fetching details for {imdb_id}: {e}")
                        continue
            else:
                logging.error(f"No results found on page {page}: {data.get('Error')}")
                break

            page += 1

    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}")

    new_shows.sort(key=lambda x: x["release_date"], reverse=True)
    logging.info(f"Found {len(new_shows)} new shows")
    return new_shows[:15]
from datetime import datetime
import requests
from config import API_KEY

def getNameFromLink(imdb_link):
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
        print(f"Request error: {e}")
        return None

def getLatestEpisode(link):
    imdbID = link.split("/")[-2]
    url = f"https://www.omdbapi.com/?i={imdbID}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data.get('Response') == 'True':
            return data.get('Title'), data.get('totalSeasons')
        else:
            raise Exception(f"Error fetching data: {data.get('Error')}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None, None


def fetchNewShowsFromIMDB(min_date, min_score):
    new_shows = []
    page = 1

    try:
        while len(new_shows) < 15:
            url = f"https://www.omdbapi.com/?apikey={API_KEY}&s=series&type=series&page={page}"
            response = requests.get(url)
            data = response.json()

            if data.get("Response") == "True":
                for item in data.get("Search", []):
                    imdb_id = item.get("imdbID")
                    try:
                        show_details = requests.get(f"https://www.omdbapi.com/?apikey={API_KEY}&i={imdb_id}").json()
                        release_date_raw = show_details.get("Released", "1900-01-01")
                        if release_date_raw == "N/A":
                            release_date = "1900-01-01"
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
                        print(f"Error fetching details for {imdb_id}: {e}")
                        continue
            else:
                print(f"No results found on page {page}: {data.get('Error')}")
                break

            page += 1

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    new_shows.sort(key=lambda x: x["release_date"], reverse=True)
    return new_shows[:15]




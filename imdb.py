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


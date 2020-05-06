from clue.util import hideOriginalQuery
import requests
from bs4 import BeautifulSoup


IMDB_MOVIE_URL = 'https://www.imdb.com/search/title/'


def getMovieClues(query):
    try:
        page = requests.get(
            IMDB_MOVIE_URL, params={
                'title': query,
                'title_type': 'feature',
                'user_rating': '7.5,',
                'num_votes': '20000,',
                'languages': 'en',
                'sort': 'moviemeter,desc'
            }
        )
        soup = BeautifulSoup(page.content, 'html.parser')
        names = soup.select("div.lister-item-content > h3 > a")

        if not names:
            return None

        title = ""
        # If the movie's name is less than two words, it is not a good clue
        for title_element in names:
            if title_element.text.count(" ") >= 2:
                title = title_element.text
                break

        if not title or query not in title.upper():
            return None

        return hideOriginalQuery(query, title + " (Movie)")
    except Exception as e:
        print(e)
        return None

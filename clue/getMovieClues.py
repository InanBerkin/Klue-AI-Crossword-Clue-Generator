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
                'num_votes': '150000,',
                'languages': 'en',
                'sort': 'moviemeter,desc'
            }
        )
        soup = BeautifulSoup(page.content, 'html.parser')
        names = soup.select("div.lister-item-content > h3")
        directors = soup.select(
            "div.lister-item-content > p:nth-child(5)")

        if not names:
            return None

        title = ""
        director = ""
        # If the movie's name is less than two words, it is not a good clue
        for i, title_element in enumerate(names):
            text = title_element.text[2:]
            if text.count(" ") >= 3:
                title = text
                title = title.replace(
                    '\n', " ").strip().replace(".", "").strip()
                director = directors[i].text.split("|")[0].strip()
                director = director[10:]
                break

        if not title or query not in title.upper():
            return None

        return hideOriginalQuery(query, title + ", Directed by " + director)
    except Exception as e:
        print(e)
        return None

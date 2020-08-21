from clue.util import isWordInText
import html
import requests
from nltk.stem.porter import *
stemmer = PorterStemmer()

GOOGLE_URL = 'https://kgsearch.googleapis.com/v1/entities:search'
API_KEY = "GOOGLE API KEY HERE"


def getGoogleKnowledgeClues(query):
    try:
        params = {
            'query': query,
            'indent': True,
            'key': API_KEY,
        }
        response = requests.get(GOOGLE_URL, params).json()['itemListElement']
        search_item = None

        for item in response:
            name = item['result']['name']
            if isWordInText(query, name):
                search_item = item['result']
                break

        if search_item is None:
            for item in response:
                wordsInName = item['result']['name'].split()
                stems = list(map(stemmer.stem, wordsInName))
                if query.lower() in stems:
                    search_item = item['result']
                    break

        if search_item is None:
            return None

        basic_description = search_item['description'] if 'description' in search_item else None
        detailed_description = ""

        if 'detailedDescription' in search_item:
            detailed_description = search_item['detailedDescription']['articleBody'].split(".")[
                0]
            return html.unescape(detailed_description) if detailed_description.count(" ") > 1 else None
        return html.unescape(basic_description) if basic_description and basic_description.count(" ") > 1 else None
    except Exception as e:
        print(e)
        print("Nothing in Google Knowledge")

import requests
import json
import urllib
import re
from bs4 import BeautifulSoup
from tokenizer import *
import inflect
import enchant
from nltk.stem.porter import *

spell_checker = enchant.Dict("en_US")
inflect = inflect.engine()
stemmer = PorterStemmer()

URL = "http://localhost:3000/answers"
GOOGLE_URL = 'https://kgsearch.googleapis.com/v1/entities:search'
DICTIONARY_URL = 'https://www.dictionary.com/browse/'
OXFORD_URL = 'https://www.lexico.com/en/definition/'
WORDNET_URL = 'https://en-word.net/json/lemma/'
IMDB_MOVIE_URL = 'http://www.omdbapi.com/?apikey=7759058a&s='
IMDB_PERSON_URL = 'https://www.imdb.com/search/name/?name='
WIKIPEDIA_URL = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=description%7Cextracts&list=&titles='
API_KEY = "***REMOVED***"

headers = requests.utils.default_headers()
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'


def compareWords(word1, word2):
    filtered_word1 = re.sub("[^a-zA-Z0-9_\.]", "", word1).upper()
    filtered_word2 = re.sub("[^a-zA-Z0-9_\.]", "", word2).upper()
    return filtered_word1 == filtered_word2


def getSuggestions(query):
    # TRY KOED
    page = requests.get(OXFORD_URL + query.replace(" ",
                                                   "_"), allow_redirects=False)
    soup = BeautifulSoup(page.content, 'html.parser')

    # for x in page.history:
    #     print(x.url)
    # print(page.url)

    suggestion_element = soup.select_one(
        "ul.search-results > li:nth-child(1) > a")
    if suggestion_element is None:
        return None
    suggestion = suggestion_element.text
    if compareWords(suggestion, query):
        return suggestion
    else:
        return None


def preprocessAnswer(word):
    # Check alternatives
    fixed_word = getSuggestions(word)
    if fixed_word:
        return fixed_word
    else:
        return stemmer.stem(word).upper()


def postprocessClue(query, original_query, clue):
    # getPluralDescription
    if inflect.plural(query).upper() == original_query.upper():
        return (query, getPluralDescription(clue))
    return (query, clue)


def checkIfEnglish(word):
    fixed_word = word
    if not spell_checker.check(word):
        suggestions = spell_checker.suggest(word)
        for suggestion in suggestions:
            if re.sub(" ", "", suggestion).upper() == word:
                fixed_word = suggestion
                break
    return fixed_word


def filterNones(arr):
    return [x for x in arr if x is not None]


def prettyPrint(d):
    print(json.dumps(d, indent=2))


def hideOriginalQuery(query, sentence):
    return re.sub(
        '(?i)' + query, '____', sentence)


def getGoogleClues(query):
    try:
        params = {
            'query': query,
            'indent': True,
            'key': API_KEY,
        }
        url = GOOGLE_URL + '?' + urllib.parse.urlencode(params)
        response = requests.get(url).json()['itemListElement']
        search_item = None

        for item in response:
            wordsInName = item['result']['name'].split()
            stems = list(map(stemmer.stem, wordsInName))
            if query.lower() in stems:
                search_item = item['result']
                break

        if search_item is None:
            return None

        basic_description = ""
        detailed_description = ""

        basic_description = search_item['description'] if 'description' in search_item else None
        if 'detailedDescription' in search_item:
            detailed_description = search_item['detailedDescription']['articleBody'].split(".")[
                0]
            return detailed_description
        return basic_description
    except Exception as e:
        print(e)
        print("Nothing in Google Knowledge")


def getDictionaryClues(query):
    def getDefinition(soup):
        desc = soup.select_one("div.css-kg6o37.e1q3nk1v3")
        if desc is None:
            return None
        return desc.text

    def getIdiom(soup):
        idiom_element = soup.select_one("section.css-sr8tkc.e1w1pzze0")
        if idiom_element is None:
            return None
        idiom = idiom_element.text.split(";")[0]
        return idiom

    try:
        page = requests.get(DICTIONARY_URL + query, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.select_one(
            "#top-definitions-section > div.css-b8jc62.e1rg2mtf5 > h1")
        if title is None or title.text != query.lower():
            return []
        return filterNones([getDefinition(soup), getIdiom(soup)])
    except Exception as e:
        print(e)
        print("Nothing in Dictionary")


def getWordNetClues(query: str):
    try:
        autocompletedQuery = requests.get(
            "https://en-word.net/autocomplete/lemma/" + query).json()
        if not autocompletedQuery:
            return None

        autocompletedQuery = autocompletedQuery[0]['item']
        if autocompletedQuery.upper() != query:
            return None
        response = requests.get(
            WORDNET_URL + autocompletedQuery, headers=headers).json()
        for lemma in response:
            if lemma['pos'] == 'n':
                if ";" in lemma['definition']:
                    return lemma['definition'].split(";")[1]
    except Exception as e:
        print(e)


def getMovieClues(query):
    try:
        page = requests.get(
            "https://www.imdb.com/search/title/?title="+query+"&title_type=feature&user_rating=7.0,&num_votes=5000,&languages=en")
        soup = BeautifulSoup(page.content, 'html.parser')
        names = soup.select("div.lister-item-content > h3 > a")
        if not names:
            return None

        title = ""
        for title_element in names:
            if title_element.text.count(" ") >= 2:
                title = title_element.text
                break

        if not title or query not in title.upper():
            return None

        return hideOriginalQuery(query, title + " (Movie)")
        # return result
    except Exception as e:
        print(e)


def getGoogleFamousPersonClues(query):
    try:
        params = {
            'query': query,
            'limit': 3,
            'indent': True,
            'key': API_KEY,
            'types': ['Person']
        }
        url = GOOGLE_URL + '?' + urllib.parse.urlencode(params)
        response = [x for x in requests.get(
            url).json()['itemListElement'] if query in x['result']['name']][0]['result']

        detailed_description = ""
        basic_description = ""

        basic_description = response['description'] if 'description' in response else ""
        if 'detailedDescription' in response:
            detailed_description = response['detailedDescription']['articleBody']
            return detailed_description
    except:
        print("Nothing in Google Knowledge Famous People")


def getFamousPersonClues(query):
    try:
        page = requests.get(IMDB_PERSON_URL + query +
                            "&groups=oscar_nominee", headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        name = soup.select_one(
            "#main > div > div.lister-list > div:nth-child(1) > div.lister-item-content > h3 > a").text.strip()
        person_info = soup.select_one(
            "#main > div > div.lister-list > div:nth-child(1) > div.lister-item-content > p.text-muted.text-small").contents
        title = person_info[0].strip()
        movie = person_info[3].text.strip()
        result = title + " in " + movie + ", " + name
        return result
    except:
        print("Nothing in IMDB Person")


def getWikipediaClues(query):
    try:
        intro = requests.get(
            WIKIPEDIA_URL + query + "&desccontinue=0&exsentences=5&exintro=1&explaintext=1").json()['query']['pages']
        intro = list(intro.values())[0]['extract']
        return intro
    except Exception as e:
        print("Nothing in Wikipedia")


def getOxfordDictionaryClues(query):
    try:
        page = requests.get(OXFORD_URL + query.replace(" ", "_"))
        soup = BeautifulSoup(page.content, 'html.parser')
        desc = soup.select_one("span.ind")
        if desc is None:
            return None
        return desc.text
    except:
        print("Nothing in Oxford")


def getAllClues(query):
    if query is None:
        print("Error: Query is None")
        return
    print("Getting clues for", query)
    clues = []
    # print("Wikipedia:")
    # clue = getWikipediaClues(query)
    # print(clue)
    # clues.append(clue)
    print("\nGoogle:")
    clue = getGoogleClues(query)
    print(clue)
    clues.append(clue)
    # print("\nDictionary:")
    # clue = getDictionaryClues(query)
    # print(clue)
    # clues.extend(clue)
    print("\nOxford:")
    clue = getOxfordDictionaryClues(query)
    print(clue)
    clues.append(clue)
    print("\nWordNet:")
    clue = getWordNetClues(query)
    print(clue)
    clues.append(clue)
    print("\nIMDb Movie:")
    clue = getMovieClues(query)
    print(clue)
    clues.append(clue)
    # Only search if nothing else is left, for performance it is disabled
    if not clues:
        print("\nIMDb Person:")
        clue = getFamousPersonClues(query)
        print(clue)
        clues.append(clue)

    clues = filterNones(clues)

    if not clues:
        print("\nNo clues found for", query)
        new_clue = getAllClues(preprocessAnswer(query))
        if new_clue:
            return new_clue
        else:
            return None

    best_clue = clues[0]

    return (query, best_clue)


# query, clue = getAllClues("TYPES")
# print(postprocessClue(query, "TYPES", clue))

def generateNewClues():
    response = requests.get(URL)
    across = response.json()['across']
    down = response.json()['down']
    result = []

    for data in across + down:
        original_query = data['answer']
        query, clue = getAllClues(original_query)
        processedClue = postprocessClue(query, original_query, clue)
        result.append((query, original_query, processedClue, data['clue']))

    prettyPrint(result)
    return result


def testSingleWord(query):
    original_query = query
    query, clue = getAllClues(original_query)
    processedClue = postprocessClue(query, original_query, clue)
    prettyPrint((original_query, processedClue))
    getNominalDescription(processedClue[1], query)


"""
WOVE
LAGER
FLAME
REC
OVALS
"""
testSingleWord('FRIZZ')
# generateNewClues()

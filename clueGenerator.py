import requests
import json
import urllib
import re
from bs4 import BeautifulSoup
from tokenizer import *
import inflect
import enchant
from nltk.stem.porter import *
import csv
import html

spell_checker = enchant.Dict("en_US")
inflect = inflect.engine()
stemmer = PorterStemmer()

URL = "http://localhost:3000/answers"
GOOGLE_URL = 'https://kgsearch.googleapis.com/v1/entities:search'
OXFORD_URL = 'https://www.lexico.com/en/definition/'
WORDNET_URL = 'https://en-word.net/json/lemma/'
IMDB_MOVIE_URL = 'http://www.omdbapi.com/?apikey=7759058a&s='
IMDB_PERSON_URL = 'https://www.imdb.com/search/name/?name='
MERRIAM_URL = 'https://dictionaryapi.com/api/v3/references/collegiate/json/'
THESAURUS_URL = 'https://www.dictionaryapi.com/api/v3/references/thesaurus/json/'
API_KEY = "***REMOVED***"

headers = requests.utils.default_headers()
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

# UTIL FUNCTIONS


def isPluralForm(single, plural):
    return compareWords(inflect.plural(single), plural)


def filterNones(arr):
    return [x for x in arr if x is not None]


def prettyPrint(d):
    print(json.dumps(d, indent=2))


def compareWords(word1, word2):
    filtered_word1 = re.sub("[^a-zA-Z0-9_\.]", "", word1).upper()
    filtered_word2 = re.sub("[^a-zA-Z0-9_\.]", "", word2).upper()
    return filtered_word1 == filtered_word2


def isWordInText(word, text):
    return any([True for word_in_name in text.upper().split()
                if compareWords(word.upper(), word_in_name)])


def hideOriginalQuery(query, sentence):
    return re.sub(
        '(?i)' + query, '____', sentence)


def getSuggestions(query):
    suggestions = []
    # suggestions = [word for word in spell_checker.suggest(
    #     query) if compareWords(word, query) and word.upper() != query.upper()]
    suggestions.append(stemmer.stem(query).upper())
    suggestions.append(query[:1] + " " + query[1:])
    suggestions.append(query[:1] + "-" + query[1:])
    suggestions.append(query[:2] + " " + query[2:])
    suggestions.append(query[:1] + "\'" + query[1:])
    return suggestions


def postprocessClue(original_query, query, clue):
    if not clue:
        return (query, None)
    if ";" in clue:
        clue = clue.split(";")[0]
    if isWordInText(query, clue):
        return getNominalDescription(clue, query)
    if inflect.plural(query).upper() == original_query.upper():
        return "(Plural) " + clue
    return clue


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

        basic_description = ""
        detailed_description = ""

        basic_description = search_item['description'] if 'description' in search_item else None
        if 'detailedDescription' in search_item:
            detailed_description = search_item['detailedDescription']['articleBody'].split(".")[
                0]
            return html.unescape(detailed_description) if detailed_description.count(" ") > 1 else None
        return html.unescape(basic_description) if basic_description and basic_description.count(" ") > 1 else None
    except Exception as e:
        print(e)
        print("Nothing in Google Knowledge")


def getWordNetClues(query: str):
    try:
        autocompletedQuery = requests.get(
            "https://en-word.net/autocomplete/lemma/" + query).json()
        if not autocompletedQuery:
            return None

        autocompletedQuery = autocompletedQuery[0]['item']
        if autocompletedQuery.upper() != query.upper():
            return None
        response = requests.get(
            WORDNET_URL + autocompletedQuery, headers=headers).json()
        for lemma in response:
            if lemma['pos'] == 'n':
                return lemma['definition']
    except Exception as e:
        print(e)


def getMovieClues(query):
    try:
        page = requests.get(
            "https://www.imdb.com/search/title/?title="+query+"&title_type=feature&user_rating=7.5,&num_votes=20000,&languages=en")
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


def getOxfordDictionaryClues(query):
    try:
        page = requests.get(OXFORD_URL + query.replace(" ", "_"))
        soup = BeautifulSoup(page.content, 'html.parser')
        desc = soup.select_one("span.ind")
        headword = soup.select_one(
            ".breadcrumbs > p:nth-child(1) > a:nth-child(5)").text
        if desc is None:
            return None
        if isPluralForm(headword, query):
            return "(Plural) " + desc.text
        return desc.text
    except:
        print("Nothing in Oxford")


def getMerriamClues(query):
    dict_key = "?key=06ecdce1-1712-4c0d-8a41-c84b717372cd"
    thesaurus_key = "?key=a77064dd-cb30-4dbd-99e3-d18a1c57b090"

    try:
        response = requests.get(MERRIAM_URL + query + dict_key).json()
        if type(response[0]) is str:
            return None

        # Past tense verb
        if 'cxs' in response[0] and response[0]['cxs'][0]['cxl'] == "past tense of":
            return "past tense of " + response[0]['cxs'][0]['cxtis'][0]['cxt']

        if not response[0]['shortdef'][0]:
            return None

        # If the query is fixed by the dictionary
        headword = normalizeText(response[0]['hwi']['hw'])
        if not isPluralForm(headword, query) and not compareWords(query, headword):
            return None

        clue = ""

        # Find clues that don't contain the word
        # Ex: strum(noun) -> an act, instance, or sound of strumming
        for alternative_meaning in response:
            short_def = alternative_meaning['shortdef'][0]
            if ";" in short_def:
                short_def = short_def.split(";")[0]
            words_in_definition = short_def.split()
            stems = list(map(stemmer.stem, words_in_definition))
            if query.lower() not in stems:
                clue = short_def
                break

        # Say it if it is an abbreviation
        abbreviation_text = "(Abbreviation) " if response[0]['fl'] == "abbreviation" else ""

        if isPluralForm(headword, query) and response[0]['fl'] == "noun":
            # clue = getPluralDescription(clue)
            clue = "(Plural) " + clue

        return abbreviation_text + clue
    except Exception as e:
        print(e)


def getAllClues(query):
    def isClueViable(clue):
        # Filter clues that are too long
        return clue and clue.count(" ") <= 25

    if query is None:
        print("Error: Query is None")
        return

    clue = None
    print("Getting clues for", query)

    print("\nIMDb Movie:")
    clue = getMovieClues(query)
    print(clue)
    if isClueViable(clue):
        return clue

    print("\nMerriam:")
    clue = getMerriamClues(query)
    print(clue)
    if isClueViable(clue):
        return clue

    print("\nOxford:")
    clue = getOxfordDictionaryClues(query)
    print(clue)
    if isClueViable(clue):
        return clue

    print("\nWordNet:")
    clue = getWordNetClues(query)
    print(clue)
    if isClueViable(clue):
        return clue

    print("\nGoogle:")
    clue = getGoogleClues(query)
    print(clue)
    if isClueViable(clue):
        return clue
    # Only search if nothing else is left, for performance it is disabled
    if not clue:
        print("\nIMDb Person:")
        clue = getFamousPersonClues(query)
        if isClueViable(clue):
            return clue

    return clue


def generateNewCrosswordCluesForQuery(query):
    clue = getAllClues(query)
    suggestions = []

    if not clue:
        suggestions = getSuggestions(query)
        for suggested_query in suggestions:
            suggested_clues = getAllClues(suggested_query)
            if suggested_clues:
                return (suggested_query, suggested_clues)

    if not clue:
        print("No clue found for", query)
        return (None, None)

    return(query, clue)


def generateNewClues():
    response = requests.get(URL)
    across = response.json()['across']
    down = response.json()['down']
    result = []

    for data in across + down:
        original_query = data['answer']
        altered_query, clue = generateNewCrosswordCluesForQuery(original_query)
        processed_clue = postprocessClue(original_query, altered_query, clue)
        result.append((altered_query, processed_clue, data['clue']))

    prettyPrint(result)
    return result


def testSingleWord(query):
    original_query = query
    altered_query, clue = generateNewCrosswordCluesForQuery(original_query)
    processed_clue = postprocessClue(original_query, altered_query, clue)
    return((original_query, altered_query, processed_clue))


generateNewClues()


# print(testSingleWord("INAPP"))
# print(getSuggestions('ILOST'))

# words = ['ADDON',
#          'ADELE',
#          'ADORE',
#          'AGREE',
#          'ALPS',
#          'AMAZE',
#          'AMORE',
#          'ANEW',
#          'ANIME',
#          'AORTA',
#          'ARAB',
#          'ARGO',
#          'AROSE',
#          'BRAYS',
#          'BREW',
#          'BRIE',
#          'BRINE',
#          'CASE',
#          'CHIA',
#          'CLEAN',
#          'CLUE',
#          'COMET',
#          'CREME',
#          'DAY',
#          'DESUS',
#          'DEUCE',
#          'DIGIN',
#          'DIGIT',
#          'DIP',
#          'DIS',
#          'DOOR',
#          'DUFF',
#          'DUSK',
#          'EARTH',
#          'EDAM',
#          'ENEMY',
#          'EYES',
#          'FADS',
#          'FAST',
#          'FINCH',
#          'FLAME',
#          'FLEAS',
#          'FORME',
#          'FORTY',
#          'FRIZZ',
#          'GAP',
#          'GAS',
#          'GENZ',
#          'GHOST',
#          'GIFT',
#          'GNOME',
#          'GREEN',
#          'GRR',
#          'GUANO',
#          'HEADY',
#          'HELLO',
#          'HERB',
#          'HOST',
#          'IBEAM',
#          'IDAHO',
#          'IDS',
#          'IGLOO',
#          'ILOST',
#          'INAPP',
#          'INDUS',
#          'INSUM',
#          'IOWAN',
#          'IRIS',
#          'ISIS',
#          'JAYZ',
#          'JOKER',
#          'KINDA',
#          'KIT',
#          'KOED',
#          'LACKS',
#          'LAGER',
#          'LARGE',
#          'LIGHT',
#          'MEMOS',
#          'MOP',
#          'MYBAD',
#          'NOFUN',
#          'NYC',
#          'OKING',
#          'ONE',
#          'OPERA',
#          'OUTER',
#          'OVAL',
#          'OVEN',
#          'PAULO',
#          'PEATY',
#          'PIT',
#          'PITT',
#          'POPE',
#          'RAT',
#          'REC',
#          'RIND',
#          'RINSE',
#          'RISK',
#          'ROBOT',
#          'SAFER',
#          'SCRAM',
#          'SET',
#          'SIN',
#          'SIRI',
#          'SISI',
#          'SLAG',
#          'SMH',
#          'SNORE',
#          'SONY',
#          'STAG',
#          'STEM',
#          'STORM',
#          'STRUM',
#          'TADA',
#          'TEASE',
#          'TEES',
#          'TEN',
#          'TENSE',
#          'TETE',
#          'THUMB',
#          'TIE',
#          'TOWIT',
#          'TWO',
#          'TYPES',
#          'ULTRA',
#          'VEGAN',
#          'WAX',
#          'WOLF',
#          'WOMB',
#          'WONKA',
#          'WORDS',
#          'WOVE',
#          'XMEN',
#          'YKNOW',
#          'ZAGS',
#          'ZEBRA',
#          'ZETAS',
#          'ZLOTY',
#          'ZZZ']


# f = open('all_clues.csv', 'w')
# writer = csv.DictWriter(f, fieldnames=['Original', 'New', 'Clue'])
# writer.writeheader()
# with f:
#     for word in words:
#         try:
#             data = testSingleWord(word)
#             writer.writerow(
#                 {'Original': data[0], 'New': data[1], 'Clue': data[2]})
#         except:
#             print("Error")
#             writer.writerow(
#                 {'Original': word, 'New': 'ERROR', 'Clue': 'ERROR'})

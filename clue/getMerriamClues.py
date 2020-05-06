import requests
from nltk.stem.porter import *
from clue.util import normalizeText
from clue.util import isPluralForm
from tokenizer import getPluralDescription

DICT_KEY = "f8a91591-5926-41b2-bd54-cb5ae3a13acd"
THESAURUS_KEY = "a77064dd-cb30-4dbd-99e3-d18a1c57b090"
stemmer = PorterStemmer()


def getClueWithNoQuery(query, definitions):
    # Find clues that don't contain the original word
    # Ex: strum(noun) -> an act, instance, or sound of strumming
    for alternative_definition in definitions:
        short_def = alternative_definition['shortdef'][0]
        if ";" in short_def:
            short_def = short_def.split(";")[0]
        words_in_definition = short_def.split()
        stems = list(map(stemmer.stem, words_in_definition))
        if query.lower() not in stems:
            return short_def


def getMerriamDictionaryClues(query):
    response = requests.get(
        f"https://dictionaryapi.com/api/v3/references/collegiate/json/{query}",
        params={
            "key": DICT_KEY
        }
    )
    clue = ""
    jsonResponse = response.json()

    if len(jsonResponse) == 0 or type(jsonResponse[0]) is str:
        return None

    # Past tense verb
    if 'cxs' in jsonResponse[0] and jsonResponse[0]['cxs'][0]['cxl'] == "past tense of":
        return "past tense of " + jsonResponse[0]['cxs'][0]['cxtis'][0]['cxt']

    if not jsonResponse[0]['shortdef']:
        return None

    clue = getClueWithNoQuery(query, jsonResponse)
    headword = normalizeText(jsonResponse[0]['hwi']['hw'])

    if isPluralForm(headword, query):
        clue = getPluralDescription(clue)
    # Say it if it is an abbreviation
    elif jsonResponse[0]['fl'] == "abbreviation":
        clue = "Abbreviation of " + clue

    return clue


def findFromMWThesaurus(word):
    response = requests.get(
        f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{word}",
        params={
            "key": THESAURUS_KEY
        }
    )

    jsonResponse = response.json()
    if len(jsonResponse) != 0:
        try:
            synonym = jsonResponse[0]["meta"]["syns"][0][0]
        except Exception:
            synonym = None
        try:
            antonym = jsonResponse[0]["meta"]["ants"][0][0]
        except Exception:
            antonym = None

        return synonym, antonym
    else:
        return None, None

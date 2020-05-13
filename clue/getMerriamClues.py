import requests
from nltk.stem.porter import *
from clue.util import normalizeText
from clue.util import isPluralForm
from clue.util import compareWords
from clue.tokenizer import getPluralDescription

DICT_KEY = "f8a91591-5926-41b2-bd54-cb5ae3a13acd"
THESAURUS_KEY = "a77064dd-cb30-4dbd-99e3-d18a1c57b090"
stemmer = PorterStemmer()


def getClueWithNoQuery(query, definitions):
    # Find clues that don't contain the original word
    # Ex: strum(noun) -> an act, instance, or sound of strumming
    for alternative_definition in definitions:
        defs = alternative_definition['shortdef']
        for short_def in defs:
            if ";" in short_def:
                short_def = short_def.split(";")[1]
            words_in_definition = short_def.split()
            stems = list(map(stemmer.stem, words_in_definition))
            headword = normalizeText(alternative_definition['hwi']['hw'])
            if stemmer.stem(query.lower()) not in stems and compareWords(stemmer.stem(query), headword):
                return (short_def, headword, alternative_definition['fl'])
    return(None, None, None)


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
        return "Past tense of " + jsonResponse[0]['cxs'][0]['cxtis'][0]['cxt']

    if not jsonResponse[0]['shortdef']:
        return None

    clue = jsonResponse[0]['shortdef'][0]
    headword = normalizeText(jsonResponse[0]['hwi']['hw'])
    pos_tag = jsonResponse[0]['fl']

    if clue is None:
        return None
    if isPluralForm(headword, query) and pos_tag == "noun":
        clue = getPluralDescription(clue)
    elif isPluralForm(headword, query) and pos_tag == "verb":
        clue = "3rd person present: " + clue
    # Say it if it is an abbreviation
    elif jsonResponse[0]['fl'] == "abbreviation":
        clue = "Abbreviation of " + clue

    return clue

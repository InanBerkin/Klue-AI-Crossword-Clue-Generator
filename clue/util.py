import inflect
import re
import json

inflect = inflect.engine()


def normalizeText(text):
    text = re.sub("[^a-zA-Z0-9_\- ]", "", text)
    return re.sub("  ", " ", text)


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

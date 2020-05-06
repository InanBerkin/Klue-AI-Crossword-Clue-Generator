import nltk
from nltk.corpus import wordnet as wn


def getWordnetClues(query):
    antonym, definition, example_sentence = None, None, None
    # nltk.download("wordnet", quiet=True)

    synsets = wn.synsets(query)
    if len(synsets) != 0:
        synset = synsets[0]
        lemma = synset.lemmas()[0]

        if lemma.antonyms():
            antonym = lemma.antonyms()[0].name()
        if synset.definition():
            definition = synset.definition()
        if synset.examples():
            example_sentence = synset.examples()[0]

    return antonym, definition, example_sentence

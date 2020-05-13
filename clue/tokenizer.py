import nltk
from clue.util import *
from nltk.chunk import *
from nltk.chunk.regexp import *
import re
import inflect
from nltk.corpus import stopwords
from nltk.stem.porter import *

inflect = inflect.engine()
stop_words = set(stopwords.words('english'))


def compareWords(word1, word2):
    filtered_word1 = re.sub("[^a-zA-Z0-9]", "", word1).upper()
    filtered_word2 = re.sub("[^a-zA-Z0-9]", "", word2).upper()
    return filtered_word1 == filtered_word2


def hideOriginalQuery(query, sentence):
    return re.sub(
        '(?i)' + query, '____', sentence)


def normalizeText(text):
    # text = re.sub("[^a-zA-Z0-9_\- ]", "", text)
    return re.sub("  ", " ", text)


def tree2text(tree):
    return normalizeText(" ".join([x[0] for x in tree.flatten()]))


def getPluralDescription(text):
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)

    chunk_rule = ChunkRule("<DT>?<JJ.?>?<NN>+", "Chunk nouns with determiner")
    chink_rule = ChinkRule("<DT>", "Remove Determiner")

    chunk_parser = RegexpChunkParser(
        [chunk_rule, chink_rule], chunk_label="Singular Description")
    chunked = chunk_parser.parse(tagged, trace=True)

    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Singular Description'):
        subtree[-1:] = [(inflect.plural(subtree[-1][0]), "Plural")]
        break

    tokens = nltk.word_tokenize(tree2text(chunked))
    tokens = [w for w in tokens if not w.lower() in ['a', 'an']]

    return " ".join(tokens)


def getNominalDescription(text, subject):
    if not isWordInText(subject, text):
        return text
    # text = text.split(",")[0]
    tokens = nltk.word_tokenize(text)
    # tokens = [w for w in tokens if not w.lower() in ['is', 'a']]
    tagged = nltk.pos_tag(tokens)

    for i, tag in enumerate(tagged):
        if compareWords(tag[0].upper(), subject):
            tagged[i] = (subject, "SUB")

    chunk_rule = ChunkRule("<SUB><.*>*", "Subject Description")
    chink_rule = ChinkRule("<VB(Z|D)><DT>", "Split by the determiner")

    chunk_parser = RegexpChunkParser(
        [chunk_rule, chink_rule], chunk_label="Nominal")

    chunked = chunk_parser.parse(tagged)
    subtrees = list(chunked.subtrees(filter=lambda t: t.label() == 'Nominal'))

    if not subtrees:
        return None

    if len(subtrees) < 2 and len(subtrees[0]) > 2:
        return tree2text(subtrees[0])

    # Ex: Cadbury Creme Egg -> Cadbury ____ Egg
    if len(subtrees[0]) > 1:
        return hideOriginalQuery(subject, " ".join([tag[0] for tag in tagged]))
    elif len(subtrees) == 2:
        return tree2text(subtrees[1])
    else:
        return None


def filterMultipleMeanings(text):
    text = text.rsplit(" or ", 1)
    text.sort(key=len, reverse=True)
    description = text[0]
    if description[-1] == ',':
        description = description[:-1]
    return(description.strip())

import nltk
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
    text = re.sub("[^a-zA-Z0-9_\- ]", "", text)
    return re.sub("  ", " ", text)


def tree2text(tree):
    return normalizeText(" ".join([x[0] for x in tree.flatten()]))


def getPluralDescription(text):
    tokens = nltk.word_tokenize(text)
    tokens = [w for w in tokens if not w.lower() in ['a', 'an']]
    tagged = nltk.pos_tag(tokens)

    chunk_rule = ChunkRule("<DT>?<JJ.?>?<NN>+", "Chunk nouns with determiner")
    chink_rule = ChinkRule("<DT>", "Remove Determiner")

    chunk_parser = RegexpChunkParser(
        [chunk_rule], chunk_label="Singular Noun")
    chunked = chunk_parser.parse(tagged, trace=True)

    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Singular Noun'):
        subtree[:] = [(inflect.plural(subtree[-1][0]), "Plural")]
        break

    return tree2text(chunked)


def getNominalDescription(text, subject):
    tokens = nltk.word_tokenize(text)
    # tokens = [w for w in tokens if not w.lower() in ['is', 'a']]
    tagged = nltk.pos_tag(tokens)

    for i, tag in enumerate(tagged):
        if compareWords(tag[0].upper(), subject):
            tagged[i] = (subject, "SUB")

    chunk_rule = ChunkRule("<SUB><.*>*", "Subject Description")
    chink_rule = ChinkRule("<VB.*><DT>", "Split by the determiner")

    chunk_parser = RegexpChunkParser(
        [chunk_rule, chink_rule], chunk_label="Nominal")

    chunked = chunk_parser.parse(tagged, trace=True)
    subtrees = list(chunked.subtrees(filter=lambda t: t.label() == 'Nominal'))

    if len(subtrees[0]) < 2:
        return None
    # Ex: Cadbury Creme Egg -> Cadbury ____ Egg
    if len(subtrees[0]) > 1:
        return hideOriginalQuery(subject, " ".join([tag[0] for tag in tagged]))
    else:
        return tree2text(subtrees[1])
    # for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Nominal'):
    #     return tree2text(subtree)


def filterEloborateDefinitions(text):
    # Descriptions with "that, which"
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    # print([tag[1] for tag in tagged])
    has_whdeterminer = "WDT" in [tag[1] for tag in tagged]

    if not has_whdeterminer:
        return text

    chunk_rule = ChunkRule("<.*>*<WDT>", "Description")
    chink_rule = ChinkRule("<WDT>", "Remove wh-determiner")

    chunk_parser = RegexpChunkParser(
        [chunk_rule, chink_rule], chunk_label="Description")

    chunked = chunk_parser.parse(tagged, trace=True)

    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Description'):
        return tree2text(subtree)


# text = "X-Men Legends II Rise of Apocalypse is an action role-playing game developed primarily by Raven Software and published by Activision"
# print(getNominalDescription(text, 'XMEN'))
# print(compareWords("X-Men", 'XMEN'))

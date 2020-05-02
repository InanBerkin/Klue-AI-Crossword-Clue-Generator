import nltk
from nltk.chunk import *
from nltk.chunk.regexp import *
import re
import inflect
from nltk.corpus import stopwords
from nltk.stem.porter import *

inflect = inflect.engine()
stop_words = set(stopwords.words('english'))


def normalizeText(text):
    text = re.sub("[^a-zA-Z0-9_\- ]", "", text)
    return re.sub("  ", " ", text)


def tree2text(tree):
    return normalizeText(" ".join([x[0] for x in tree.flatten()]))


def isPerson(text):
    tagged = nltk.pos_tag([text.capitalize()])
    namedEnt = nltk.ne_chunk(tagged)
    print(namedEnt)
    return namedEnt[0].label() == "PERSON"


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
    tokens = [w for w in tokens if not w in ['is']]
    tagged = nltk.pos_tag(tokens)

    # print(" ".join([x[0] for x in tagged]))

    for i, tag in enumerate(tagged):
        if tag[0].upper() == subject:
            tagged[i] = (subject, "SUB")

    # namedEnt = nltk.ne_chunk(tagged)
    # print(namedEnt)

    chunk_rule = ChunkRule("<SUB><.*>*", "Subject Description")
    chink_rule = ChinkRule("<SUB><V.*>?<DT>?<NN.*>*", "Remove Subjects")

    chunk_parser = RegexpChunkParser(
        [chunk_rule, chink_rule], chunk_label="Nominal")
    chunked = chunk_parser.parse(tagged, trace=True)

    print()
    for subtree in chunked.subtrees(filter=lambda t: t.label() == 'Nominal'):
        print(tree2text(subtree))

# subject = "AMI"
# text = "Brine is a high-concentration solution of salt in water"
# text = "Edam is a mild yellow Dutch cheese made in balls encased in a red covering"
# text = "Brie is a soft cow's-milk cheese named after Brie, the French region from which it originated"
# text = "TOWIT is a free, global, cross-platform mobile app, website, and Web API that allows civilians to report parking violations and dangerous driving in real-time"
# text = "TETE is the capital city of TETE Province in Mozambique"
# text = "AMI is a town located in Ibaraki Prefecture, Japan"
# getNominalDescription(text, subject)

# stemmer = PorterStemmer()
# stem = stemmer.stem("KOED")
# print(stem)
# print(nltk.pos_tag(["KOED"]))

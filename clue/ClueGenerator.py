from clue.getMerriamClues import getMerriamDictionaryClues
from clue.getMovieClues import getMovieClues
from clue.getGoogleKnowledgeClues import getGoogleKnowledgeClues
from clue.getMusenetClues import getMusenetClues
from clue.getWordnetClues import getWordnetClues
from clue.getOxfordDictionaryClues import getOxfordDictionaryClues
from concurrent.futures import ThreadPoolExecutor
from clue.util import isWordInText
from clue.util import hideOriginalQuery
from clue.util import prettyPrint
from tokenizer import getNominalDescription
from nltk.stem.snowball import *
import requests
stemmer = SnowballStemmer("english")

MAX_WORD_COUNT = 25


def run_io_tasks_in_parallel(tasks):
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()


class ClueGenerator():
    def __init__(self, original_query):
        self.original_query = original_query
        self.definitions = set()
        self.synonyms = set()
        self.antonyms = set()
        self.example_sentences = set()
        self.new_clues = []

    def generateNewClues(self, query=None):
        if query is None:
            query = self.original_query
        self.searchMerriamDictionary(query)
        run_io_tasks_in_parallel([
            lambda: self.searchImdb(query),
            # lambda: self.searchMerriamDictionary(query),
            lambda: self.searchGoogleKnowledge(query),
            lambda: self.searchMusenet(query),
            lambda: self.searchOxfordDictionary(query),
        ])
        print("Finished getting clues")
        self.preprocessClues()
        self.sortNewClues()
        return self.getBestClue()

    def generateSuggestions(self):
        suggestions = set()
        query = self.original_query
        suggestions.add(stemmer.stem(query).upper())
        suggestions.add(query[:1] + " " + query[1:])
        suggestions.add(query[:1] + "-" + query[1:])
        suggestions.add(query[:2] + " " + query[2:])
        suggestions.add(query[:2] + "-" + query[2:])
        suggestions.add(query[:1] + "\'" + query[1:])
        return suggestions

    def searchOxfordDictionary(self, query):
        print("Searching Oxford Dictionary")
        source = "oxford"
        definition = getOxfordDictionaryClues(query)
        if definition:
            self.definitions.add((definition, source))

    def searchMerriamDictionary(self, query):
        print("Searching Merriam Webster Dictionary")
        source = "mw"
        definition = getMerriamDictionaryClues(query)
        if definition:
            self.definitions.add((definition, source))

    def searchImdb(self, query):
        print("Searching IMDB")
        movie = getMovieClues(query)
        if movie:
            clue = hideOriginalQuery(query, movie)
            self.new_clues.append((clue, 'movie', 'imdb'))

    def searchGoogleKnowledge(self, query):
        print("Searching Google Knowledge")
        source = "knowledge"
        definition = getGoogleKnowledgeClues(query)
        if definition:
            nominal_form = getNominalDescription(definition, query)
            if nominal_form:
                self.definitions.add((nominal_form, source))
            else:
                self.definitions.add((definition, source))

    def searchMusenet(self, query):
        print("Searching Musenet")
        synonym = getMusenetClues(query)
        if synonym:
            self.synonyms.add((synonym, 'muse'))

    def searchWordnet(self, query):
        source = "wordnet"
        antonym, definition, example_sentence = getWordnetClues(query)
        if antonym:
            self.antonyms.add((antonym, source))
        if definition:
            self.definitions.add((definition, source))
        if example_sentence:
            self.example_sentences.add((example_sentence, source))

    def preprocessClues(self):
        self.preprocessDefinitions()
        self.preprocessSynonyms()
        self.preprocessAntonyms()

    def preprocessDefinitions(self):
        for definition in self.definitions:
            definition_text, source = definition[0], definition[1]
            if definition_text.count(" ") < MAX_WORD_COUNT and not isWordInText(self.original_query, definition_text):
                self.new_clues.append((definition_text, "definition", source))

    def preprocessSynonyms(self):
        for synonym in self.synonyms:
            synonym, source = synonym[0], synonym[1]
            clue = "Similiar to " + synonym.lower()
            self.new_clues.append((clue, "synonym", source))

    def preprocessAntonyms(self):
        for antonym in self.antonyms:
            antonym, source = antonym[0], antonym[1]
            clue = "Opposite of " + antonym.lower()
            self.new_clues.append((clue, "synonym", source))

    def getBestClue(self):
        if len(self.new_clues) != 0:
            return self.new_clues[0][0]
        else:
            print(f"Error: No clue found for {self.original_query}")
            return None

    def sortNewClues(self):
        sourceSorting = [
            "imdb",
            "wordnet",
            "mw",
            "oxford",
            "muse",
            "knowledge"
        ]

        categorySorting = [
            "movie",
            "definition",
            "synonym",
            "antonym",
            "example-sentence"
        ]

        try:
            self.new_clues = sorted(self.new_clues, key=lambda x: (
                sourceSorting.index(x[2]), categorySorting.index(x[1])))
        except Exception as e:
            print(e)
            print("Error while sorting")
            pass


def getClue(query):
    clueGenerator = ClueGenerator(query)
    best_clue = clueGenerator.generateNewClues()
    if best_clue:
        return best_clue
    else:
        suggestions = clueGenerator.generateSuggestions()
        for suggestion in suggestions:
            clueGenerator = ClueGenerator(suggestion)
            best_clue = clueGenerator.generateNewClues()
            if best_clue:
                return best_clue


def getAllClues():
    URL = "http://localhost:3000/answers"
    response = requests.get(URL)
    across = response.json()['across']
    down = response.json()['down']
    result = []

    for data in across + down:
        original_query = data['answer']
        print("Searching clue for", original_query)
        best_clue = getClue(original_query)
        result.append((None, best_clue, data['clue']))

    return result


print(getClue("ISIS"))
# prettyPrint(getAllClues())

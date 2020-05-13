from clue.getMerriamClues import getMerriamDictionaryClues
from clue.getMovieClues import getMovieClues
from clue.getGoogleKnowledgeClues import getGoogleKnowledgeClues
from clue.getThesaurusClues import getThesaurusClues
from clue.getWordnetClues import getWordnetClues
from clue.getOxfordDictionaryClues import getOxfordDictionaryClues
from concurrent.futures import ThreadPoolExecutor
from clue.util import isWordInText
from clue.util import hideOriginalQuery
from clue.util import prettyPrint
from clue.tokenizer import getNominalDescription
from clue.tokenizer import filterMultipleMeanings
import requests

MAX_WORD_COUNT = 15


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
        self.searchThesaurus(query)
        run_io_tasks_in_parallel([
            lambda: self.searchImdb(query),
            lambda: self.searchGoogleKnowledge(query),
            lambda: self.searchOxfordDictionary(query),
        ])
        print("Finished getting clues")
        self.preprocessClues()
        self.sortNewClues()
        return self.getBestClue()

    def generateSuggestions(self):
        suggestions = set()
        query = self.original_query
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
            self.definitions.add((definition, source))

    def searchThesaurus(self, query):
        print("Searching MW Thesaurus")
        synonym, antonym = getThesaurusClues(query)
        if synonym:
            self.synonyms.add((synonym, 'mw'))
        if antonym:
            self.antonyms.add((antonym, 'mw'))

    def searchWordnet(self, query):
        source = "wordnet"
        synonym, antonym, definition, example_sentence = getWordnetClues(query)
        if synonym:
            self.synonyms.add((antonym, source))
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
            if ";" in definition_text:
                definition_text = definition_text.split(
                    ";")[1].strip().replace(".", "")
            print("Making (", definition_text[:10], ") ...nominal form")
            nominal_form = getNominalDescription(
                definition_text, self.original_query)
            if nominal_form:
                definition_text = nominal_form
            if definition_text.count(" ") < MAX_WORD_COUNT and self.original_query not in definition_text.upper():
                self.new_clues.append((definition_text, "definition", source))

    def preprocessSynonyms(self):
        for synonym in self.synonyms:
            synonym, source = synonym[0], synonym[1]
            clue = synonym.lower()
            self.new_clues.append((clue, "synonym", source))

    def preprocessAntonyms(self):
        for antonym in self.antonyms:
            antonym, source = antonym[0], antonym[1]
            clue = "Opposite of " + antonym.lower()
            self.new_clues.append((clue, "antonym", source))

    def postprocessClue(self):
        for i, clue in enumerate(self.new_clues):
            self.new_clues[i] = [
                filterMultipleMeanings(clue[0]), clue[1], clue[2]]

    def getBestClue(self):
        if len(self.new_clues) != 0:
            print("\nAll Clues for", self.original_query)
            prettyPrint(self.new_clues)
            print()
            return self.new_clues[0][0]
        else:
            print(f"Error: No clue found for {self.original_query}")
            return None

    def sortNewClues(self):
        sourceSorting = [
            "imdb",
            "oxford",
            "mw",
            "wordnet",
            "knowledge",
        ]

        categorySorting = [
            "movie",
            "definition",
            "synonym",
            "antonym",
            "example-sentence"
        ]

        try:
            self.postprocessClue()
            self.new_clues = sorted(self.new_clues, key=lambda x: (
                sourceSorting.index(x[2]), categorySorting.index(x[1])
            ))
        except Exception as e:
            print(e)
            print("Error while sorting")
            pass


def getClue(query):
    clueGenerator = ClueGenerator(query)
    best_clue = clueGenerator.generateNewClues()
    if best_clue:
        return best_clue.capitalize()
    else:
        suggestions = clueGenerator.generateSuggestions()
        for suggestion in suggestions:
            clueGenerator = ClueGenerator(suggestion)
            best_clue = clueGenerator.generateNewClues()
            if best_clue:
                return best_clue.capitalize()


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
        if best_clue:
            result.append(
                (original_query, best_clue.capitalize(), data['clue']))
        else:
            result.append((original_query, 'No Clue', data['clue']))

    return result


# print(getClue("ISIS"))
# prettyPrint(getAllClues())

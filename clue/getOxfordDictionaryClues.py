import requests
from bs4 import BeautifulSoup
from clue.util import isPluralForm
from tokenizer import getPluralDescription

OXFORD_URL = 'https://www.lexico.com/en/definition/'


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
            return getPluralDescription(desc.text)
        return desc.text
    except:
        print("Nothing in Oxford")

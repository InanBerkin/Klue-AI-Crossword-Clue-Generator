import requests


def getThesaurusClues(query):
    try:
        response = requests.get(
            f"https://dictionaryapi.com/api/v3/references/thesaurus/json/{query}",
            params={
                "key": 'a77064dd-cb30-4dbd-99e3-d18a1c57b090'
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
    except:
        pass

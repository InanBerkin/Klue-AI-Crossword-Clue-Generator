import requests


def getMusenetClues(query):
    try:
        THRESHOLD = 80000
        response = requests.get(
            "https://api.datamuse.com/words",
            params={
                "ml": query
            }
        )
        jsonResponse = response.json()
        if len(jsonResponse) != 0 and "score" in jsonResponse[0] and jsonResponse[0]["score"] >= THRESHOLD:
            return jsonResponse[0]["word"]
        else:
            return None
    except:
        pass

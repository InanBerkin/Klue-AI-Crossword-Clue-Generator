import flask
import json
from flask_cors import CORS, cross_origin
from clue.ClueGenerator import getAllClues

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

clues = []


@app.route("/")
@cross_origin()
def helloWorld():
    global clues
    if not clues:
        clues = getAllClues()
    response = json.dumps(clues)
    return response


app.run(port=3001)

from flask import Flask, render_template, request, flash ,session,send_file
import base64
import json
from search import SearchEngine

global search

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')

@app.route('/search/<method>/<term>',methods=['GET'])
def search_api(method, term):
    global search
    result, matches, records = search.search({method: True, 'TERM': term}, smartdecode=True)
    content = request.json
    result = {
        "result": result,
        "matches": matches,
        "records": records
    }
    return json.dumps(result), 200, {'content-type':'application/json'}

@app.route('/refresh',methods=['GET'])
def refresh_index():
    global search

    print("Directory indexing started...")
    search=SearchEngine("index.pkl")
    search.create_new_index({'PATH':'C://Users/Dell/Downloads'})
    print("Directory indexing completed...")

refresh_index()
if __name__ == '__main__':
    app.run(host= '127.0.0.1', debug=True, )
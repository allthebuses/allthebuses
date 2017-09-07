import os
import requests
from flask import Flask, jsonify
from flask_compress import Compress
import mimetypes

GOOG_API_KEY=os.environ['GOOG_API_KEY']
SHEET_ID=os.environ['SHEET_ID']
SHEET_RANGE=os.environ['SHEET_RANGE']

goog_api = requests.Session()
goog_api.params = { 'key': GOOG_API_KEY }

app = Flask(__name__)
Compress(app)

mimetypes.add_type("application/vnd.geo+json", ".geojson")
app.config['COMPRESS_MIMETYPES'].append("application/vnd.geo+json")

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/ridden-by')
def root():
    return app.send_static_file('by-person.html')

@app.route('/status.json')
def status():
    result = goog_api.get('https://sheets.googleapis.com/v4/spreadsheets/' +
            SHEET_ID + '/values/' + SHEET_RANGE)

    return jsonify(result.json()['values'])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

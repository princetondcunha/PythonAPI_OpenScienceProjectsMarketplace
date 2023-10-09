'''Main'''

import json
from flask import Flask, request, jsonify
from Libs.util import *

app = Flask(__name__)


@app.route('/embed_owner',methods=['PUT'])
def embed_owner():
    '''Embed Owner'''
    email_owner = request.get_json().get('emailId')
    embed_update_owner(email_owner)
    response = {
        'message': 'The owner has been embedded',
        'status': 'success'
    }
    return jsonify(response)

@app.route('/embed_collab',methods=['PUT'])
def embed_collab():
    '''Embed Collab'''
    email_collab = request.get_json().get('emailId')
    embed_update_collab(email_collab)
    response = {
        'message': 'The collaborator has been embedded',
        'status': 'success'
    }
    return jsonify(response)

@app.route('/cossim',methods=['POST'])
def cossim():
    '''Cosine Similarity'''
    email_owner = request.get_json().get('emailId')
    return jsonify(cosine_similarity(email_owner,invoker_collab_all()))

@app.route('/prompt',methods=['POST'])
def prompt_response():
    '''Prompt Response'''
    email_owner = request.get_json().get('owner')
    email_collab = request.get_json().get('collaborator')
    parse=parser_survey(invoker_owner(email_owner),invoker_collab(email_collab))
    response = {"response": prompt_on_similarity(parse)}
    json_response = json.dumps(response)
    return json_response, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True)

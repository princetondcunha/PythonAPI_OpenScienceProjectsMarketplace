'''Util'''

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import openai
from numpy import dot
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

uri = os.getenv("MONGO_LOGIN")
client = MongoClient(uri, server_api=ServerApi('1'))

#Parsing Owner Data
def parser_owner(owner_cursor):
    '''Parser Owner'''
    parsed_data = f"Company Description: {owner_cursor['description']}, Skills Required: {', '.join(owner_cursor['techStack'])}, Expected scope of work :{owner_cursor['expectedScopeOfWork']}, Expected timeline to do project :{owner_cursor['expectedTimeline']}"
    return parsed_data

#Parsing Collab Data
def parser_collab(collab_cursor):
    '''Parser Collab'''
    parsed_data = f"Professional Summary: {collab_cursor['professionalSummary']}, Skills Possessed: {', '.join(collab_cursor['skills'])}, Project Interested In :{collab_cursor['typesOfProject']}, Availability :{collab_cursor['availability']}"
    return parsed_data

#Embedding Function
def embeddings(to_embedd):
    '''Embeddings'''
    response = openai.Embedding.create(model="text-embedding-ada-002", input=to_embedd)
    return [data.embedding for data in response.data][0]

#Cosine Similarity
def cosine_similarity(owner_email,embedded_user_info):
    '''Cosine Similarity'''
    cosine_similarities = []
    embedded_user_data = []
    embedded_id_data = []

    owner_data = invoker_owner(owner_email)
    embedded_owner_data = owner_data['embeddingsData']

    #Split the embedded value and ID value to perform cosine similarity
    for user_id, embed_value in embedded_user_info:
        embedded_user_data.append(embed_value)
        embedded_id_data.append(user_id)

    #Comparing cosine values
    for data in embedded_user_data:
        cosine_similarities.append(dot(embedded_owner_data, data)*100)
    #Converting array into a list to sort and send ID back
    #cosine_float = [float(arr[0]) for arr in cosine_similarities]
    mapped_list = list(zip(embedded_id_data, cosine_similarities))
    sorted_list = sorted(mapped_list, key=lambda x: x[1], reverse = True)
    return sorted_list[:10]

#Prompt about similarity
def prompt_on_similarity(query):
    '''Prompt on Similarity'''
    response = openai.Completion.create(
        model = "gpt-3.5-turbo-instruct",
        prompt = query,
        temperature=1,
        max_tokens=256,
        top_p=1)
    return response['choices'][0]['text']

#Cosine Similarity ID List
def get_first_elements(tuple_list):
    '''Get First Elements'''
    return [t[0] for t in tuple_list]

#Parsing Query Data
def parser_survey(owner_cursor, collab_cursor):
    '''Parser Survey'''
    parsed_data = f"Tell me why this Job Description {owner_cursor['expectedScopeOfWork']} with Skills Required such as {', '.join(owner_cursor['techStack'])} and expected timeline to complete project is {owner_cursor['expectedTimeline']} matches with the candidate having Professional Summary: {collab_cursor['professionalSummary']} and Skills such as {', '.join(collab_cursor['skills'])}, who is interested in project such as {collab_cursor['typesOfProject']}, with availability to start project {collab_cursor['availability']}"
    return parsed_data

def invoker_owner(email_id):
    '''Invoker Owner'''
    db = client["nasa"]
    #Owner Data
    owner_collection = db["owners"]
    owner_cursor = owner_collection.find({"emailId" :email_id})
    return owner_cursor[0]

def invoker_collab(email_id):
    '''Invoker Collab'''
    db = client["nasa"]
    #Owner Data
    collab_collection = db["collaborator"]
    collab_cursor = collab_collection.find({"emailId" :email_id})
    return collab_cursor[0]

def invoker_collab_all():
    '''Embed Invoker Collab All'''
    db = client["nasa"]
    #Owner Data
    collab_collection = db["collaborator"]
    collab_cursor = collab_collection.find({})
    email_id = []
    embed_data = []
    for data in collab_cursor:
        print("Trace: ",data)
        email_id.append(data['emailId'])
        embed_data.append(data['embeddingsData'])
    mapped_list = list(zip(email_id, embed_data))
    return mapped_list

def embed_update_owner(email_id) :
    '''Embed Update Owner'''
    doc_key = {'emailId': email_id}
    embed_field = {"$set": {"embeddingsData": embeddings(parser_owner(invoker_owner(email_id)))}}
    db = client["nasa"]
    owner_collection = db["owners"]
    owner_collection.update_one(doc_key, embed_field)

def embed_update_collab(email_id) :
    '''Embed Update Collab'''
    doc_key = {'emailId': email_id}
    embed_field = {"$set": {"embeddingsData": embeddings(parser_collab(invoker_collab(email_id)))}}
    db = client["nasa"]
    collab_collection = db["collaborator"]
    collab_collection.update_one(doc_key, embed_field)


def invoker_initialize():
    '''Invoker Initialize'''
    db = client["nasa"]

    #Collab Data
    collab_collection = db["collaborator"]
    collab_cursor = collab_collection.find({})
    email_id_collab = []
    for data in collab_cursor:
        email_id_collab.append(data['emailId'])

    #Owner Data
    owner_collection = db["owners"]
    owner_cursor = owner_collection.find({})
    email_id_owner = []
    for data in owner_cursor:
        email_id_owner.append(data['emailId'])
    return email_id_owner,email_id_collab

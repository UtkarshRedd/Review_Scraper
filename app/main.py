"""The Flask App."""

# pylint: disable=broad-except

import os
import pandas as pd 
import pickle
import flask
from flask import Flask, abort, jsonify, request, render_template, send_from_directory, redirect,url_for
from werkzeug.utils import secure_filename

import sys
sys.path

from rq.job import Job

from .functions import scrape_amazon
from .functions import scrape_shopee
from .redis_resc import redis_conn, redis_queue

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
import re, string, random

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="maheshavel",
  password="2308",
  database='scrapedb'
)


app = Flask(__name__)

app.config['FILEPATH']='results'
app.config['UPLOAD_PATH'] = 'uploads'

@app.errorhandler(404)
def resource_not_found(exception):
    """Returns exceptions as part of a json."""
    return jsonify(error=str(exception)), 404


@app.route("/")
def home():
    return flask.render_template('index.html')


@app.route("/enqueue", methods=["POST", "GET"])
def enqueue():
    """Enqueues a task into redis queue to be processes.
    Returns the job_id."""
    if request.method == "GET":
        link = request.args.get("link")
        retailer = request.args.get("retailer")
        if not link or not retailer:
            abort(
                404,
                description=(
                    "Missing Parameters"
                ),
            )
        data = {"link": link,"retailer": retailer}
    if request.method == "POST":
        data = request.json

    job={}
    if retailer=="amazon":
        job=redis_queue.enqueue(scrape_amazon,data,job_timeout=500)
    else:
        job=redis_queue.enqueue(scrape_shopee,data,job_timeout=500)
        print("hello")
    print(data)
    return jsonify({"job_id": job.id})


@app.route("/check_status")
def check_status():
    """Takes a job_id and checks its status in redis queue."""
    job_id = request.args["job_id"]

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exception:
        abort(404, description=exception)

    return jsonify({"job_id": job.id, "job_status": job.get_status()})


@app.route("/get_result")
def get_result():
    """Takes a job_id and returns the job's result."""
    job_id = request.args["job_id"]

    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as exception:
        abort(404, description=exception)

    if not job.result:
        abort(
            404,
            description=f"No result found for job_id {job.id}. Try checking the job's status.",
        )
    return jsonify(job.result)


@app.route("/fetch")
def fetch():
	mycursor = mydb.cursor()
	print("Inside fetch function")
	sql="select * from review1";
	mycursor.execute(sql)
	#myresult = mycursor.fetchall()
	desc = mycursor.description
	column_names = [col[0] for col in desc]
	data = [dict(zip(column_names, row)) for row in mycursor.fetchall()]
	print(len(data))
	return jsonify(data)
	
@app.route('/results/<file_name>')
def show_post(file_name):
	return send_from_directory(app.config['FILEPATH'],file_name)
	
	
	
	
def remove_noise(tweet_tokens, stop_words = ()):
    cleaned_tokens = []
    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'
        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)
        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def ValuePredictor_file(df):
    df["Model_Rating"]=["" for i in range(len(df))]
    classifier = pickle.load(open("model.pkl","rb"))
    for index,row in df.iterrows():
        to_predict_review = str(row["Review text"])
        to_predict_tokens = remove_noise(word_tokenize(to_predict_review))
        df.loc[index, "Model_Rating"] = classifier.classify(dict([token, True] for token in to_predict_tokens))
    return df

def ValuePredictor(review):
	to_predict_review = str(review)
	to_predict_tokens = remove_noise(word_tokenize(to_predict_review))
	classifier = pickle.load(open("model.pkl","rb"))
	result = classifier.classify(dict([token, True] for token in to_predict_tokens))
	return result


@app.route('/predict',methods = ['GET'])
def result():
    if request.method == 'GET':
        review = request.args.get("review")
        result = ValuePredictor(review)
        return {"sentiment":result}


@app.route('/', methods=['POST'])
def upload_files():
    if 'file' in request.files:
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        df=pd.read_excel("uploads/"+filename);
        df=ValuePredictor_file(df)
        df.to_excel('uploads/output.xlsx',index=False)
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)
	

if __name__ == "__main__":
    app.run(debug=True)

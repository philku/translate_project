from flask import Flask, request, render_template, redirect, send_from_directory
from __main__ import *
from google.cloud import datastore
import os
import google
import csv
from importlib import reload
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.cloud import translate_v2 as translate
import requests
from email.utils import make_msgid
import uuid
import datetime

#Needed for Google Login - created by google.py
CLIENT_SECRET_FILE = "client_secret.json"
API_NAME = "gmail"
API_VERSION = "v1"
SCOPES = ["https://mail.google.com/"]

#Allows access for Google APIs without Login
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service-key.json"

client = datastore.Client()
kind = 'Studinfo'

app = Flask(__name__)   # Flask is the web framework we're using

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/hello', methods=['GET'])
def hello():
    return render_template('hello.html')

@app.route('/translateandemail', methods=['GET'])
def translateandemail():
    query = client.query(kind = "Studinfo")
    results = list(query.fetch())
    return render_template('translateandemail.html', emails=results)

@app.route('/confirmation', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        data = request.form.to_dict(flat=True)
        Email = data['myemail']
        email = Email
        studinfo_key = client.key(kind, email)
        studinfo = datastore.Entity(key=studinfo_key)
        Name = data['myname']
        Language = data['mylanguage']
        studinfo['name'] = Name
        studinfo['language'] = Language
        client.put(studinfo)
        return render_template('confirmation.html', FormEmail=Email, FormName=Name, FormLanguage=Language)   # Renders the page with the response
    else:
        # GET - Render customer creation form
        return render_template('translateandemail.html')
        
@app.route('/mailsend', methods=['POST'])
def mailsend():
    data = request.form.to_dict(flat=True)
    service1 = google.Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES) 
    emailMsg = data['mybody']
    emailSub = data['mysubject']
    #Language codes that are required by the Translate API
    lang_codes = {}
    with open("language-codes.csv", newline = "") as file:
        r = csv.reader(file, delimiter = ",")
        for row in r:
            lang_codes.update({row[1]: row[0]})
    translate_client = translate.Client()
    #Fetches Studinfo datastore database, which holds names, emails, and preferred language
    client = datastore.Client()
    query = client.query(kind = "Studinfo")
    query_iter = query.fetch()
    #Following loop runs through Studinfo database and translates email for their preferred language
    for entity in query_iter:        
        mimeMessage = MIMEMultipart()
        mimeMessage["to"] = entity.key.id_or_name
        lang = entity["language"]
        if lang != "English":
            emailSub = translate_client.translate(emailSub, target_language = lang_codes[lang])["translatedText"]
            emailMsg = translate_client.translate(emailMsg, target_language = lang_codes[lang])["translatedText"]
        #MIME is the program/API that actually talks to
        mimeMessage["subject"] = emailSub
        mimeMessage.attach(MIMEText(emailMsg, 'plain'))
        raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()
        #Actually sends email
        message = service1.users().messages().send(userId='me', body={'raw': raw_string}).execute()
        m_key = client.key("Messages")
        #This code provides the UUID and sends it to the Streaminfo database
        streamID = str(uuid.uuid1())
        d = datetime.datetime.now()
        complete_key = client.key("Streaminfo", streamID)
        contact = datastore.Entity(key=complete_key)
        contact.update({
        'email': entity.key.id_or_name,
        "studref": entity
        })
        client.put(contact)

        #Calls to above functions:

        sendMessage()
        #replyMessage(mid)
        os.remove("token_gmail_v1.pickle")

#Hosts app on localhost

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
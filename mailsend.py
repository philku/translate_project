import google
import csv
from importlib import reload
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google.cloud import datastore
from google.cloud import translate_v2 as translate
import os
import requests
from email.utils import make_msgid
import uuid
import datetime
from flask import Flask, request, render_template, redirect

app = Flask(__name__)   # Flask is the web framework we're using

#Needed for Google Login - created by google.py
CLIENT_SECRET_FILE = "client_secret.json"
API_NAME = "gmail"
API_VERSION = "v1"
SCOPES = ["https://mail.google.com/"]

#Allows access for Google APIs without Login
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "service-key.json"

#WARNING - OLD CODE - This code was used before we decided on UUID solution
#this is a function which takes an id and searches for the email thread.
#It will be used to reply to an original message    
#def replyMessage(oId):
#    user_id = "me"
#    service = google.Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
#    #tlist = service.users().threads().list(userId=user_id).execute().get('threads', [])
#    tdata = service.users().threads().get(userId=user_id, id=oId).execute()
#    msg = tdata["messages"][0]["payload"]
#    subject = ""
#    messageId = ""
#    inReplyTo = ""
#    references = ""
#    for header in msg["headers"]:
#        if header["name"] == "Subject":
#            subject = header["value"]
#        elif header["name"] == "In-Reply-To":
#            inReplyTo = header["value"]
#        elif header["name"] == "Message-ID":
#            messageId = header["value"]
#        elif header["name"] == "References":
#            references = header["value"]
#    print("Subject:", subject)
#    print("Message-ID:", messageId)
#    print("In-Reply-To:", inReplyTo)
#    print("References:", references)

#this function is used to send the original message
#currently, it sends up a followup message with the email id


#Code that interacts with Google Login Services and creates the message and subject
#The message and subject will be translated later in the process

#Matt's added code



#Regular code

def sendMessage():
    service1 = google.Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES) 
    emailMsg = "This is the message of this mail, for testing purposes"
    emailSub = "This is the subject"
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
        m_key = client.key("Messages", mId)
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


#below are the CALLS to the above functions (replyMessage is not functional yet)
#------------------------------------------------------------------------------

sendMessage()
#replyMessage(mid)
os.remove("token_gmail_v1.pickle")

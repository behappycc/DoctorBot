from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import requests
import random
import re
import time
import sys
import os
from pprint import pprint
from .models import fb_db
print (sys.path)
#sys.path.append('../brain/brain_libs/DST')
print (sys.path)
#import DST_joint_model


#@ensure_csrf_cookie
verify_token = '11111111'
TOKEN = 'EAAG1BsKUxZB8BALNakB02SE5R3tAf7NyEXF8plOF1SUKkvWWiHwvmi2OoQBqcOqCjJxfRkC9wR7t3kIYv3AfQaZBOTJwfpQQtL7eIMA4z9fhLmApLEDF25iZA99U3RZBZA9WQRnHK7mWjGvmcER2sTZBFo0Ln9AqT8hluFZA5hPGQZDZD'

# Create your views here.
json_dir = "../brain/brain_libs/DST/user_data/"
class Doctor(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    pprint(message)
                    if 'text' not in message['message']:
                        break
                    savetodb(message,message['message']['text'],message['sender'])
                    time.sleep(0.5)
                    post_facebook_message(message['sender']['id'])
        return HttpResponse()

    def get(self, request):#, *args, **kwargs):
        print("=======")
        print(request.build_absolute_uri() )
        print("print")
        print(self.request.GET['*'])
        if self.request.GET['hub.verify_token'] == verify_token:

            print("print") 
            print(self.request.GET['*'])
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error,invalid token')

def savetodb(message,text,sender_id):
    sender_id = json.dumps(sender_id)
    fb_db.objects.create(content = sender_id,title=text)
    fbid=""
        
    for i in range(8,len(sender_id)-2):
        fbid += str(sender_id[i])



def post_facebook_message(fbid):
    print("fbid")
    print(fbid)
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % TOKEN

    json_path = json_dir + "DM_" + fbid+ ".json"
    time.sleep(0.5) 
    #while True:
    with open(json_path,'r') as json_file:
        line = json.load(json_file)
    text = line['Sentence'] 
    #        continue
    print(line['Sentence'])
    if True:
   #     for k, v in line.items():
   #         text = text + str(k) + " " + str(v) + '\n'
        with open(json_path,'w') as json_file:
            json.dump(line,json_file)
   #        break
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": text}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
           


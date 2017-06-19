from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import http.client, urllib.request, urllib.parse, urllib.error, base64
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
#import  get_user_name

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
        print("incoming_message")
        pprint(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' not in message:
                    break
                if 'attachments' in message['message']:
                    for payload in message['message']['attachments']:
                        print(payload['payload'])
                        print(payload['payload']['sticker_id'])
                        if payload['payload']['sticker_id']==369239263222822:
                            post_facebook(message['sender']['id'])
                        elif 'sticker' in payload['payload']: 
                            break
                        else:    
                            print(payload['payload']['url'])
                            url = payload['payload']['url']
                            face_api(url,message['sender']['id'])
                        
                elif 'text' in message['message']:
                    savetodb(message,message['message']['text'],message['sender'])
                    time.sleep(0.5)
                    post_facebook_message(message['sender']['id'])
                else: 
                     print('error')
                     break
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
    with open(json_path,'r') as json_file:
        line = json.load(json_file)
    text = line['Sentence'] 
    print(line['Sentence'])
    with open(json_path,'w') as json_file:
        json.dump(line,json_file)
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": text}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

def post_facebook(fbid):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % TOKEN
    text ='謝謝你！希望有幫助到你~~' 
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": text}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
def face_api(uri,fbid):
    print("face_api")
    headers = {
    # Request headers
    'Content-Type': 'application/json',

    # NOTE: Replace the "Ocp-Apim-Subscription-Key" value with a valid subscription key.
    'Ocp-Apim-Subscription-Key': 'aa017257cd20414188cd44f619ed9fc6',
    }

    params = urllib.parse.urlencode({
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender,smile,emotion',
    })


    try:
    # NOTE: You must use the same location in your REST call as you used to obtain your subscription keys.
    #   For example, if you obtained your subscription keys from westus, replace "westcentralus" in the 
    #   URL below with "westus".
        conn = http.client.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, "{\"url\":\""+uri+"\"}", headers)
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        describe = json.loads(data)[0]
        #text = text[0]
        print(describe)
        
        #text['faceAttributes']['emotion'])
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    print("post facebook image")
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s' % TOKEN
    text = health_res(describe)
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": text}})
    requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)

def health_res(text):
    emotion = {} 
    age = ""
    gender = ""
    smile = ""
    reply ="" 
    value = text['faceAttributes']
    print(value['smile'])
    print(value['emotion'])
    emotion = value['emotion']
    age = value['age']
    gender = value['gender']
    smile = value['smile']
    print(age)
    print(gender)
    if smile>0.5:
        text = "你看起來很開心！請問我們有甚麼可以幫助你呢？\n你可以輸入你好來看看我們有甚麼功能喔！"
        reply = reply + text
    if value['emotion']['anger'] > 0.5:
        text = "你看起來有點生氣喔，多微笑點，生活會更加美好XD \n你可以輸入你好來看看我們有甚麼功能喔！"
        reply = reply + text
    if value['emotion']['sadness'] > 0.3:
        text = "你看起來有點難過耶，怎麼了還好嗎，需要我們怎麼幫助你呢？\n你可以輸入你好來看看我們有甚麼功能喔！" 
        reply = reply + text
    # 
    if gender == 'female'  and age < 60.0 and age > 40.0:
        text = "\n你好，你現在年齡預估為"+str(age)+"歲，要注意你的身體。據統計，在你這個年齡層的女性有17%的女性在未來十年成為高風險群族，40～49歲婦女的檢查最好一年做乳房X光攝影、隔年做超音波檢查\n"
        reply = reply + text
    elif gender =='female' and age < 40.0 and age > 25.0:
        text = "\n你好，你現在年齡預估為"+str(age)+"歲，要注意你的身體。40歲以下的婦女記得做乳房超音波的檢查喔~~\n"
        reply = reply + text        

    elif gender == 'female' and age < 25.0:
        text = "\n你好，你現在年齡預估為"+str(age)+"歲，你是社會未來的希望，我們的社會需要像你一樣年輕的人才！乳癌是最容易發生在女性群族的疾病，建議你從發育開始就要養成定期檢查的習慣，每1~2年，定期至乳房專科醫師接受乳房影像學檢查，若有乳癌家族史的女性，應聽從醫師建議，每年定期檢查或按月追蹤喔~~\n"
        reply = reply + text
        
    elif gender == 'male' and age < 60.0 and age > 40.0:
        text = "\n你好，你現在年齡預估為"+str(age)+"歲，要注意你的身體。大腸癌在初期的症狀很不明顯，如果有腸胃不是或便秘，千萬不要忽略它~建議你少吃紅肉、加工食品，才不會對身體有太大的負擔~\n" 
        reply = reply + text

    elif gender =='male' and age < 40.0 and age > 25.0:
        text = "\n你好，你現在年齡預估為"+str(age)+"歲，要注意你的身體。不要以為大腸癌只發生在50歲以上的群族，也有可能發生在你身上喔。如果你有血便或是便秘的情形，要記得趕快去檢查，才不會耽擱黃金時間喔~\n"
        reply = reply + text

    elif gender =='male' and age < 25.0:
        text = "\n你好，你現在年齡預估為"+str(age)+"歲，你是國家的棟樑，國家的未來就要看你們這種菁英！但記得保持身體健康，多運動，才不會年老一身病喔！\n"
        reply = reply + text
    print(reply)
    return reply 
     

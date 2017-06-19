from django.http import HttpResponse
from django.http import HttpRequest
from django.shortcuts import render_to_response
from django.shortcuts import render
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
json_dir = "../brain/brain_libs/DST/"
input_name = "DM_website_input.json"
output_name = "DM_website_output.json"
import json
import os
import time
from website import speech_api
# Create your views here.
@api_view(['GET'])


def index_view(request):
    return render_to_response('index.html',{'data':str(json_dir+input_name),})
def query(request):
    req = request.GET['message']
    print(req)
    with open(json_dir+"user_data/"+input_name,'w') as json_file:
        json.dump({'content':req},json_file)
    time.sleep(0.5)
    with open(json_dir+"user_data/"+output_name,'r') as json_output:
        line = json.load(json_output)
    text = ""
    text = line['Sentence']
    print('text')
    print(text)
    return HttpResponse(json.dumps(text), content_type='application/json')

def ms_api(request):
    req = request.GET['status']
    print(req)
    print('get ms_api')
    with open(json_dir+"user_data/"+output_name,'r') as json_output:
        line = json.load(json_output)
    text = ""
    text = line['Sentence']
    speech_api.api_func(text)
    print('execute')
    text =  {}
    return HttpResponse(json.dumps(text), content_type='application/json')

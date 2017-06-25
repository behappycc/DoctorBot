import sys
import os
import json
import re
sys.path.append('../LU_model')
import db
sys.path.pop()
sys.path.append('../joint_model')
import get_lu_pred
sys.path.pop()
sys.path.append('../data_resource')
import CrawlerTimeTable
sys.path.pop()
sys.path.append('/user_data')
import time
import random
#import djanigo
#sys.path.append('../../../doctorbot')
#from doctorbot import settings
#from fb_doctor_chatbot import models
#setup_environ(settings)
#os.environ['DJANGO_SETTINGS_MODULE'] = 'doctorbot.settings'

DIR_NAME = '../../../../DoctorBot/doctorbot/'
import sqlite3
conn = sqlite3.connect(DIR_NAME + 'db.sqlite3')
fb = conn.cursor()
from random import shuffle
#from apscheduler.schedulers.blocking import BlockingScheduler
#from datetime import datetime


DB_IP = "104.199.131.158"  # doctorbot GCP ip
DB_PORT = 27017  # default MongoDB port
DB_NAME = "doctorbot"  # use the collection
client = db.MongoClient(DB_IP, DB_PORT)
collection_division = client[DB_NAME]["division"]
collection_disease = client[DB_NAME]["disease"]
disease = []
week = []
c_day = []
division = []
doctor = []
with open('../data_resource/disease_dict.txt', 'r', encoding='utf-8') as r_disease:
    for line in r_disease:
        disease.append(line.replace('\n',''))
with open('../data_resource/week_dict.txt', 'r', encoding='utf-8') as r_week:
    for line in r_week:
        week.append(line.replace('\n',''))
with open('../data_resource/division_dict.txt', 'r', encoding='utf-8') as r_division:
    for line in r_division:
        division.append(line.replace('\n',''))
c_day = ['今天','明天','後天']


def initialize():
    state = {"intent": None, "disease": None, "division": None, "doctor": None, "time": None}
    DM = {"Request": None, "Intent": None, "Slot": None, "State": state,"History": None}
    return DM
#################################################################################################
#                   search for division or doctor from database                                 #
#################################################################################################
##################################################
#             adding for confirm                 #
##################################################
def DM_format(DM):
    new_DM = {}
    new_DM['request'] = DM['Request']
    new_DM['intent'] = DM['Intent']
    new_DM['slot'] = DM['Slot']
    new_DM['state'] = DM['State']
    for key,value in new_DM['state'].items():
        if value == None:
            new_DM['state'][key] = []
        elif type(new_DM['state'][key]) ==str:
            new_DM['state'][key] = [value]
    if new_DM['request'] =='info':
        new_DM['request'] = 'inform'
    return new_DM

def time_C_A(time_str):
    d = int(time.strftime('%d'))
    m = int(time.strftime('%m'))
    y = int(time.strftime('%y'))+89
    w = int(time.strftime('%w'))
    pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
    match = pattern.search(time_str)
    if match!=None :
        return match
    for index,day in enumerate(week):
        if time_str ==day:
            index = (index+1)%7
            d = d + index-w
    if d >30:
        d = d%30
        m = m+1
    return(str(y)+'.'+str(m)+'.'+str(d))



def get_dbinfo(slot1,slot2, choose):
    client = db.MongoClient(DB_IP, DB_PORT)

    collection_division = client[DB_NAME]["division"]
    collection_disease = client[DB_NAME]["disease"]
    doctor_list = []
    #use disease to find division
    if slot2 == "department":
        for data in collection_disease.find({"disease_c": {"$regex": slot1}}):
            return  data['department']
    #use disease to find doctors
    elif slot2 == "doctor" and choose == 0:
        for data in collection_division.find({"$and": [{"disease": {"$regex": slot1}},
                                                       {"department": {"$regex": ""}}]}):
            for name in data['doctor']:
                if name not in doctor_list:
                    doctor_list.append(name)
        return doctor_list
    #use division to find doctors
    elif slot2 == "doctor" and choose == 1:
        for data in collection_division.find({"$and": [{"disease": {"$regex": ''}},
                                                       {"department": {"$regex": slot1}}]}):
            for name in data['doctor']:
                if name not in doctor_list:
                    doctor_list.append(name)
        return doctor_list
#################################################################################################
#                   decide a request                                                            #
#################################################################################################
def DM_request(DM):
    DM["Request"] = None
    DM["Slot"] = None

    if DM["Intent"] == 1 or DM["Intent"] == 2:
        if DM["State"]["disease"]!=None:
            DM["Request"] = "end"
            DM['History'] =='end12'
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease"]
    elif DM["Intent"] == 3:
        if DM["State"]["division"] != None and DM["State"]["disease"] != None:
            DM["Request"] = "end"
        elif DM["State"]["disease"] == None:
            DM["Request"] = "info"
            DM["Slot"] = ["disease"]
        else:
            DM["Request"] = "end"
            DM["State"]["division"] = get_dbinfo(DM["State"]["disease"], "department",0)
    elif DM["Intent"] == 4:
        if DM["State"]["doctor"] != None:
            DM["Request"] = "end"
        elif DM["State"]["disease"] != None:
            DM["State"]["doctor"] = get_dbinfo(DM["State"]["disease"], "doctor",0)
            DM["Request"] = "choose"
            DM["Slot"] = ["doctor"]
        elif DM["State"]["division"] != None:
            DM["State"]["doctor"] = get_dbinfo(DM["State"]["division"], "doctor", 1)
            DM["Request"] = "choose"
            DM["Slot"] = ["doctor"]
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease", "division", "doctor"]
    elif DM["Intent"] == 5:
        if DM["State"]["doctor"] != None and DM["State"]["time"] != None:
            DM["Request"] = "end"
        elif DM["State"]["doctor"] == None:
            if DM["State"]["disease"] != None:
                DM["State"]["doctor"] = get_dbinfo(DM["State"]["disease"], "doctor",0)
                DM["Request"] = "choose"
                DM["Slot"] = ["doctor"]
            elif DM["State"]["division"] != None:
                DM["State"]["doctor"] = get_dbinfo(DM["State"]["division"], "doctor",1)
                DM["Request"] = "choose"
                DM["Slot"] = ["doctor"]
            else:
                DM["Request"] = "info"
                DM["Slot"] = ["disease","division","doctor"]
        elif DM["State"]["time"] == None:
            if DM["State"]["doctor"] != None:
                DM["State"]["time"] = CrawlerTimeTable.Timetable(str(DM["State"]["doctor"])).get_time()
                DM["Request"] = "choose"
                DM["Slot"] = ["time"]
        else:
            DM["Request"] = "info"
            DM["Slot"] = ["disease","division","doctor"]
    else:
        pass

    return DM

def get_str(input):
    if input == None:
        return ""
    elif type(input) == list:
        return ", ".join(input)
    elif type(input) == str:
        return input
def get_ans(DM):
#    if DM["Intent"] == 1:
#        #fdaf
    if DM["Intent"] == 2:
#        DM['State']['division'] = []
        for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
            DM['State']['division'] = data['department']
    elif DM["Intent"] == 3:
#        DM["State"]['doctor'] =[]
        for data in collection_division.find({"$and": [{"disease": {"$regex": get_str(DM['State']['disease'])}},
                                                          {"department": {"$regex": get_str(DM['State']['division'])}}]}):
            DM["State"]['doctor'] = data['doctor']
    elif DM["Intent"] == 4:
        DM['State']['time'] =[]

        DM['State']['time']=CrawlerTimeTable.Timetable(get_str(DM["State"]["doctor"])).get_time()
#    elif DM["Intent"] == 5:
        #dfa
    return DM

def greeting():
    sen_list = ["哈囉我的朋友，我是seek doctor Bot，有什麼我能幫得上忙的嗎？",
                "哈囉！你好，我是seek doctor Bot，請問有什麼需要幫忙的嗎？",
                "嗨你好，我是seek doctor Bot，吃飯了沒?",
                "哈囉～我是seek doctor Bot，有什麼需要幫忙的嗎？",
                "哈囉你好，我是seek doctor Bot，請問你有醫療上的問題嗎?",
                "我是Doctor Bot，專門解決各種醫療疑難雜症，請問有什麼需要幫忙的嗎？",
                "HELLO~我是seek doctor Bot，你最近過的怎麼樣啊?",
                "你好，我是seek doctor Bot，有什麼疑難雜症需要我幫忙的嗎？Doctor Bot 在這裡使命必達！",
                "你好！今天也活力充沛嗎~我是seek doctor Bot，請問有甚麼需要幫忙的？",
                "今天過得好嗎？我是Doctor Bot，很高興為您服務！",
                "你好，我是Doctor Bot，有任何需要幫助的，都可以跟我說哦",
                "你好R，我是seek doctor Bot，可以幫你什麼呢？",
                "您好，我是Doctor Bot，今天過的如何呢？",
                "安安您好！我是seek doctor Bot!"]
    sentence = sen_list[random.randint(0, len(sen_list)-1)]
    sentence += "\n\n"
    sen_list = ["我支援的功能有", "我可以幫忙", "我能夠"]
    sentence += sen_list[random.randint(0, len(sen_list)-1)]
    sentence += "(1)查疾病的症狀, (2)查疾病的科別, (3)查醫師, (4)查門診時刻表, (5)幫忙掛號，對我說 謝謝 可以重設系統"
    return sentence

def goodbye():
    sen_list = ["祝你身體健康唷！掰掰",
                "感謝你，希望你接下來事事順心！",
                "希望下次還能再為您服務",
                "感謝使用本服務，祝平安喜樂",
                "嘻嘻，期待下次跟您對話。",
                "感謝您使用本服務，祝您事事順心！",
                "祝你有個開心的一天,掰掰~",
                "感謝您使用本服務，希望下次見面是很久以後",
                "謝謝，祝您身體健康、萬事如意，掰掰",
                "感謝您使用Doctor Bot服務",
                "謝謝您的使用",
                "預防勝於治療，要好好保養您的身體呀!祝您身體健康!",
                "謝謝您，祝你早日康復",
                "再見～再見～再說一聲下次再見～",
                "祝您身體健康一切順心，有個美好的一天",
                "祝您身體健康。",
                "感謝您使用本服務，歡迎再次光臨",
                "感謝您的使用，祝您身體健康！",
                "祝福您一切平安順遂！",
                "很高興為您服務，祝您身體健康",
                "歲月靜好，吃好睡飽，感謝您使用本服務，祝您身體健康！",
                "平安喜樂！再見"]
    sentence = sen_list[random.randint(0, len(sen_list) - 1)]
    return sentence

def info_intent():
    sen_list = ["請問您要問什麼事情呢?",
                "請問你今天需要什麼樣的服務呢？",
                "請問您要幹嘛咧？",
                "哈囉您好，請問需要哪方面的服務呢?",
                "請問你想要幹嘛呢？",
                "我目前有提供：「問疾病的症狀」、「問疾病的科別」、「問醫生」、「問門診時刻表」、「掛號」的服務，請問能幫你什麼？」",
                "有什麼需要我的地方？",
                "請問您需要什麼？",
                "請問需要什麼幫忙嗎？",
                "您想獲得哪個項目的資訊呢？",
                "請問你要「問疾病的症狀」、「問疾病的科別」、「問醫生」、「問門診時刻表」還是「掛號」呢?",
                "請問您有什麼需求呢？",
                "您有甚麼需要幫忙的嗎?我是個好幫手喔!",
                "請問今天想要找我做什麼呢？",
                "請告訴我你希望我為你做什麼呢？",
                "請問您需要甚麼服務呢？請輸入症狀、科別、醫生、門診時間、掛號等關鍵字。",
                "請問你現在是想要做什麼呢？",
                "嗨，您說您想要我提供什麼服務呢?",
                "哈囉！請問您想要使用甚麼服務呢？"]
    sentence = sen_list[random.randint(0, len(sen_list) - 1)]
    return sentence
def get_sentence(DM):
    sentence =""
    if(DM["Request"] == "end"):
        DM = get_ans(DM)
        if DM["Intent"] == 1:
            sentence += get_str(DM['State']['disease'])
            sen_list = ["的相關症狀有\n", "常見症狀有\n", "的話,通常罹患此病會常有\n",
                        "通常有下列症狀\n", "關於這個疾病。患者通常會\n"]
            sentence += sen_list[random.randint(0, len(sen_list) - 1)]
            for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
                sentence += ", ".join(data['symptom'])
            sentence += ", ".join(data['symptom'])
            sentence += "更多資訊可以到這裡看看喔；\n"
            sentence += data['url']
        elif DM["Intent"] == 2:
            sentence += get_str(DM['State']['disease'])
            sen_list = ["的科別是：\n", "的相關科別：\n", "可以去這些科別喔：\n"]
            sentence += sen_list[random.randint(0, len(sen_list) - 1)]
            for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
                sentence += ", ".join(data['department'])
        elif DM["Intent"] == 3:
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sen_list = ["的醫生有：\n", "有這些醫生：\n", "可以找這些醫生喔：\n"]
            sentence += sen_list[random.randint(0, len(sen_list) - 1)]
            for data in collection_division.find({"$and": [{"disease": {"$regex": get_str(DM['State']['disease'])}},
                                                          {"department": {"$regex": get_str(DM['State']['division'])}}]}):
                sentence += (data['department'] + " 醫師: " + ", ".join(data['doctor']))
        elif DM["Intent"] == 4:
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += get_str(DM['State']['doctor'])
            sentence += "的門診時間為：\n"
            sentence += ", ".join(CrawlerTimeTable.Timetable(get_str(DM["State"]["doctor"])).get_time())
        elif DM["Intent"] == 5:
            sen_list = ["掛號完成~是", "幫您完成掛號了喔~", "耶！掛號完成,是",
             "掛號成功了！是", "已經幫您預約好", "您好,掛號已經完成,是", "恭喜您掛號完成,是"]
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += get_str(DM['State']['doctor'])
            sentence += get_str(DM['State']['time'])
            sentence += " 的門診\n"
        sentence += "\n\n謝謝您使用Seek Doctor！希望有幫助到您！Good bye~"
    elif(DM["Request"] == "info"):
        sen_list = ["請告訴我\n ", "請問\n", "好的 請給我\n",
           "請問您找尋的\n", "請問您現在要查的\n"]
        sentence += sen_list[random.randint(0, len(sen_list) - 1)]
        for index,slot in enumerate(DM['Slot']):
            if slot == "disease":
                sentence += " 疾病名稱 "
            elif slot == "division":
                sentence += " 科別名稱 "
            elif slot == "doctor":
                sentence += " 醫生名稱 "
            if index != len(DM['Slot'])-1:
                sentence += "或"
        sentence += ",謝謝!"
    elif (DM["Request"] == "choose"):
        sen_list = ["要選哪個呢?請選擇一個吧\n", "這裡有這些可以選呢！請選擇一個吧\n", "請問您要選擇哪一個\n",
            "有這些可供選擇喔!請選擇一個吧\n", "找到了！請選擇一個吧\n"]
        sentence += sen_list[random.randint(0, len(sen_list) - 1)]
        if DM['Slot'][0] == "doctor":
            sentence += "醫生名稱："
            DM['History'] = 'c_doctor'
        elif DM['Slot'][0] == "time":
            sentence += "看診時間："
            temp = CrawlerTimeTable.Timetable(str(DM["State"]["doctor"])).get_status()
            DM['State']['time'] = CrawlerTimeTable.Timetable(str(DM["State"]["doctor"])).get_time()
#            DM['State']['time']
            for key,value in DM['State']['time']:
                sentence += value + ' '
                sentence += temp[key]+' '

        sentence += get_str(DM['State'][get_str(DM['Slot'][0])])
    elif (DM["Request"] == "confirm"):
        sentence += "你說的是" + DM["Slot"] + "?"

    #####################################################
    #                      ADDDING                      #
    #####################################################
#    elif (DM["Request"] == "confirm"):

    return sentence
def intent_LU(DM,sentence):
    if(sentence == '我要查症狀'):
        DM["Intent"] = 1
    elif(sentence =='我要查科別'):
        DM["Intent"] = 2
    elif(sentence =='我要查醫生'):
        DM["Intent"] = 3
    elif(sentence =='我要查時間'):
        DM["Intent"] = 4
    elif(sentence =='我要掛號' or sentence =='我要掛門診'or sentence =='我想要掛門診'):
        DM["Intent"] = 5
    if(DM['History'] =='end12'):
        if(sentence.find('哪科')or sentence.find('哪一科') or sentence.find('什麽科')):
            DM["Intent"] = 2
        elif(sentence.find('掛號')or sentence.find('掛門診') or sentence.find('幫我掛')):
            DM["Intent"] = 5

    return DM
def confirm(DM):
    if(DM["History"] == 'time_C_A'):
        DM['Request'] == 'confirm'
        DM['Slot'] = DM["State"]["time"]
    elif(DM["History"] == 'vague_division'):
        DM['Request'] == 'confirm'
        DM['Slot'] = DM["State"]["division"]
    DM['History'] = None
    return DM
def LU_train(DM,sentence,lu_model):
    slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}
    pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
    match = pattern.match(sentence)
    found = False
    if match:
        DM["State"]["time"] = sentence
#        DM["State"]["time"] = time_C_A(DM["State"]["time"])
    if sentence in week or sentence[:len(sentence)-1] in week :
        DM["State"]["time"] = sentence
        DM["State"]["time"] = time_C_A(DM["State"]["time"])
    for key in c_day:
        if sentence.find(key):
            DM["State"]["time"] = key
            DM["State"]["time"] = time_C_A(DM["State"]["time"])

    if sentence in division:
        DM["State"]["division"] = sentence
    elif sentence[:len(sentence)-1] in division:
        DM["State"]["division"] = sentence[:len(sentence)-1] + '部'
        DM["History"] = 'vague_division'
    elif sentence[:len(sentence)-1] + '科' in division:
        DM["State"]["division"] = sentence[:len(sentence)-1] + '部'
        DM["History"] = 'vague_division'
    if sentence in disease:
        DM["State"]["disease"] = sentence
    if found == False:
        semantic_frame = lu_model.semantic_frame(sentence)
        slot_dictionary = semantic_frame['slot']
    #Nothing found, use LU model.
    print ('[ Before LU ]')
    print (DM)
    print("[ LU ]")
    for slot, value in semantic_frame['slot'].items():
        print(slot, ": ", value)
    for slot in slot_dictionary:
        if slot_dictionary[slot] != '' and (DM["State"][slot] == None or (type(DM["State"][slot]) == list and len(DM["State"][slot]) < 1)):
            DM["State"][slot] = slot_dictionary[slot]

    if type(DM["State"]["time"]) == str and DM["State"]["time"] not in week and not match:
        DM["State"]["time"] = None

    if DM["Intent"] == None:
        DM["Intent"] = int(semantic_frame['intent'])
        DM['State']['intent'] = [str(DM['Intent'])]
    print("Intent : ", DM["Intent"])
    return DM
#def job(fb):
#    print (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
#    init = fb.fetchall()
#    return init

def main():

    sys.stdout.flush()
    DM = initialize()
    disease = []
    week = []
    division = []
    doctor = []
    with open('../data_resource/disease_dict.txt', 'r', encoding='utf-8') as r_disease:
        for line in r_disease:
            disease.append(line.replace('\n',''))
    with open('../data_resource/week_dict.txt', 'r', encoding='utf-8') as r_week:
        for line in r_week:
            week.append(line.replace('\n',''))
    with open('../data_resource/division_dict.txt', 'r', encoding='utf-8') as r_division:
        for line in r_division:
            division.append(line.replace('\n',''))
    lu_model = get_lu_pred.LuModel()

    fb = conn.cursor()
    print("waiting for the fb input...")
    fb.execute('select * from fb_doctor_chatbot_fb_db')
    init = fb.fetchall()
    while True:
    #website user DM
        #with open("user_data/DM_website_input.json",'r') as f:
        #    ff = json.load(f)
        #sentence_web = ff['content']
   # while True:
        #if buff == sentence_web:
        #    continue
        #else:
        #    print('not equal')
        #    print(sentence_web)
        #    buff = sentence_web
        #    if os.path.exists("user_data/DM_website_output.json"):
        #        with open("user_data/DM_website_output.json",'r') as f:
        #            DM_web = json.load(f)
        #            print("\nload DM_web success\n")

        #    else:
        #        with open("user_data/DM_website_output.json",'w') as f:
        #            DM_web = initialize()
        #            DM_web['Sentence'] = "你好，我是seek doctor Bot，我支援的功能有(1)查症狀, (2)查科別, (3)查醫師, (4)查時間, (5)幫我掛號，並可以用 謝謝 重設系統"
        #            json.dump(DM_web,f)
        #            print("save DM_web success")
        #    slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}
        #    if True:
        #        if True:
        #            if sentence_web == '謝謝' or sentence_web == '你好' or sentence_web == '嗨':
        #                DM_web = initialize()
        #                DM_web['Sentence'] = "你好，我是seek doctor Bot，我支援的功能有(1)查症狀, (2)查科別, (3)查醫師, (4)查時間, (5)幫我掛號，並可以用 謝謝 重設系統"
        #                with open('./user_data/DM_website_output.json','w') as f_w:
        #                    json.dump(DM_web,f_w)
        #                    print("update DM_web success")
        #                continue
        #            if DM_web['Request'] == 'end':
        #                DM_web = initialize()
        #            slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}
        #            pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
        #            match = pattern.match(sentence_web)
        #            print(sentence_web)
        #            if match:
        #                DM_web["State"]["time"] = sentence_web
        #                print('1')
        #            elif sentence_web in week:
        #                print('2')
        #                DM_web["State"]["time"] = sentence_web
        #            elif sentence_web in division:
       # #                print('3')
        #                DM_web["State"]["division"] = sentence_web
        #            elif sentence_web in disease:
        #                print('4')
        #                DM_web["State"]["disease"] = sentence_web
        #                #semantic_frame = lu_model.semantic_frame(sentence)
        #                #slot_dictionary = semantic_frame['slot']
        #            else:
        #                semantic_frame = lu_model.semantic_frame(sentence_web)
        #                slot_dictionary = semantic_frame['slot']
        #            print ('[ Before LU ]')
        #            print (DM_web)
        #            print("[ LU ]")
        #            for slot, value in semantic_frame['slot'].items():
        #                print(slot, ": ", value)
        #            for slot in slot_dictionary:
        #                if slot_dictionary[slot] != '' and (DM_web["State"][slot] == None or (type(DM_web["State"][slot]) == list and len(DM_web["State"][slot]) > 1)):
        #                    DM_web["State"][slot] = slot_dictionary[slot]

        #            if type(DM_web["State"]["time"]) == str and DM_web["State"]["time"] not in week and not match:
        #                DM_web["State"]["time"] = None

        #            if DM_web["Intent"] == None:
        #                DM_web["Intent"] = int(semantic_frame['intent'])
        #            print("Intent : ", DM_web["Intent"])
        #            DM_web = DM_request(DM_web)
        #            DM_web_nlg = DM_web
        #            DM_web_nlg['Sentence'] = get_sentence(DM_web)
        #            print ("[ DM_web ]")
        #            for i in DM_web_nlg:
        #                print (i, DM_web_nlg[i])
        #            with open("user_data/DM_website_output.json", 'w') as fp:
        #                json.dump(DM_web_nlg, fp)
        #                print("save succeed.")
        #fb = conn.cursor()
        fb.execute('select MAX(ID) from fb_doctor_chatbot_fb_db')
        new_id = fb.fetchone()[0]
        multi_id=[]     #ids' list
        fb.execute('select * from fb_doctor_chatbot_fb_db ')
        after = fb.fetchall()
        after = list(sorted(set(after)-set(init)))  #只要這次執行DST.py之後的FB輸入
        if not after :
            continue
        else:
            after.sort(key=lambda tup:tup[0])
            print("after")
            print(after)
            mess = after.pop(0)
            print(mess)
            sender_id = mess[1]
            name = sender_id[8:-2]
            sentence = mess[3]
            init.append(mess)
            if True:
                 if True:
                    if os.path.exists("./user_data/DM_"+name+".json"):    #如果此sender id之前有輸入的話就讀取裡面內容
                        with open("user_data/DM_"+name+".json", 'r') as f:
                            DM = json.load(f)
                            print ("\nLoad DM Success.\n")
                    else:
                        with open("user_data/DM_"+name+".json",'w') as f:
                            DM = initialize()
                            DM['Sentence'] = greeting()
                            #DM['Sentence'] = "你好，我是seek doctor Bot，我支援的功能有(1)查症狀, (2)查科別, (3)查醫師, (4)查時間, (5)幫我掛號，並可以用 謝謝 重設系統"
                            json.dump(DM,f)
                            print('write json DM')
                    slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}
                    user_greeting = ['嗨', '你好', '您好', '哈囉', '安安', 'hi', 'Hi', '嗨嗨', '早安',
                                     '午安', '晚安', '早上好', '勢早', 'Hello', 'hello']
                    user_ending = ['謝謝', '掰掰','掰','okbye', '結束', '再見', 'bye', '好掰掰', '拜拜',
                                   '感謝', '好窩', '謝啦', '你真棒', '謝惹','再會','你可以走了']
                    if sentence in user_greeting or sentence in user_ending:
                        DM = initialize()
                        DM['Sentence'] = greeting()
                        #DM['Sentence'] = "你好，我是seek doctor Bot，我支援的功能有(1)查症狀, (2)查科別, (3)查醫師, (4)查時間, (5)幫我掛號，並可以用 謝謝 重設系統"
                        with open('./user_data/DM_'+name+'.json','w') as f_w:
                            json.dump(DM,f_w)
                            print("update DM success")
                        continue

#                    DM =LU_train(DM,sentence,lu_model)
                    DM = intent_LU(DM,sentence)
                    DM = DM_request(DM)
                    DM = confirm(DM)
                    DM_nlg = DM
                    DM_nlg['Sentence'] = get_sentence(DM)
                    print ("[ DM ]")
                    for i in DM_nlg:
                        print (i, DM_nlg[i])
                    with open("user_data/DM_"+name+".json", 'w') as fp:
                        json.dump(DM_nlg, fp)
                        print("save succeed.")
        time.sleep(0.5) #wait 0.5 secone to listen to if a fb new data stored.
    time.sleep(0.5)

if __name__ == '__main__':
    main()

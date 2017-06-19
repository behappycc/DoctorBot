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

def initialize():
    state = {"intent": None, "disease": None, "division": None, "doctor": None, "time": None}
    DM = {"Request": None, "Intent": None, "Slot": None, "State": state}
    return DM
#################################################################################################
#                   search for division or doctor from database                                 #
#################################################################################################
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

def greeting():
    greeting_template = ["哈囉我的朋友，我是seek doctor Bot，有什麼我能幫得上忙的嗎？",
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
    sentence = greeting_template[random.randint(0, len(greeting_template)-1)]
    sentence += "\n"
    sen_list = ["我支援的功能有", "我可以幫忙", "我能夠"]
    sentence += sen_list[random.randint(0, len(sen_list)-1)]
    sentence += "(1)查疾病的症狀, (2)查疾病的科別, (3)查醫師, (4)查門診時刻表, (5)幫忙掛號，對我說 謝謝 可以重設系統"
    return sentence

def goodbye():
    goodbye = ["祝你身體健康唷！掰掰",
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
    sentence = goodbye[random.randint(0, len(goodbye) - 1)]
    return sentence

def get_sentence(DM):
    sentence =""
    if(DM["Request"] == "end"):
        if DM["Intent"] == 1:
            sentence += get_str(DM['State']['disease'])
            sentence += "的相關症狀有：\n"
            for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
               sentence += ", ".join(data['symptom'])
        elif DM["Intent"] == 2:
            sentence += get_str(DM['State']['disease'])
            sentence += "的相關科別為：\n"
            for data in collection_disease.find({"disease_c": {"$regex": get_str(DM['State']['disease'])}}):
                sentence += ", ".join(data['department'])
        elif DM["Intent"] == 3:
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += "的醫生有：\n"
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
            sentence += "已幫您預約掛號 "
            sentence += get_str(DM['State']['division'])
            sentence += get_str(DM['State']['disease'])
            sentence += get_str(DM['State']['doctor'])
            sentence += get_str(DM['State']['time'])
            sentence += " 的門診\n"
        sentence += "\n\n"
        sentence += goodbye()
    elif(DM["Request"] == "info"):
        sentence += "請告訴我"
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
        sentence += "請選擇一個"
        if DM['Slot'][0] == "doctor":
            sentence += "醫生名稱："
        elif DM['Slot'][0] == "time":
            sentence += "看診時間："
        sentence += get_str(DM['State'][get_str(DM['Slot'][0])])
    return sentence

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
                    if sentence in user_greeting:
                        DM = initialize()
                        DM['Sentence'] = greeting()
                        #DM['Sentence'] = "你好，我是seek doctor Bot，我支援的功能有(1)查症狀, (2)查科別, (3)查醫師, (4)查時間, (5)幫我掛號，並可以用 謝謝 重設系統"
                        with open('./user_data/DM_'+name+'.json','w') as f_w:
                            json.dump(DM,f_w)
                            print("update DM success")
                        continue
                    if DM['Request'] == 'end':
                        DM = initialize()
                    slot_dictionary = {'disease': '', 'division': '', 'doctor': '', 'time': ''}
                    pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+")
                    match = pattern.match(sentence)
                    if match:
                        DM["State"]["time"] = sentence
                    elif sentence in week:
                        DM["State"]["time"] = sentence
                    elif sentence in division:
                        DM["State"]["division"] = sentence
                    elif sentence in disease:
                        DM["State"]["disease"] = sentence
                    else:
                        semantic_frame = lu_model.semantic_frame(sentence)
                        slot_dictionary = semantic_frame['slot']
                    print ('[ Before LU ]')
                    print (DM)
                    print("[ LU ]")    
                    for slot, value in semantic_frame['slot'].items():
                        print(slot, ": ", value)
                    for slot in slot_dictionary:
                        if slot_dictionary[slot] != '' and (DM["State"][slot] == None or (type(DM["State"][slot]) == list and len(DM["State"][slot]) > 1)):
                            DM["State"][slot] = slot_dictionary[slot]

                    if type(DM["State"]["time"]) == str and DM["State"]["time"] not in week and not match:
                        DM["State"]["time"] = None

                    if DM["Intent"] == None:
                        DM["Intent"] = int(semantic_frame['intent'])
                    print("Intent : ", DM["Intent"])
                    DM = DM_request(DM)
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

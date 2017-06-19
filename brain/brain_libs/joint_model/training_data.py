"""

Usage:
python3 training_data.py
**disease.csv and division.csv are in the folder ../data_resource/

Output:
data/source_sentence.txt
data/source_slot.txt
data/source_intent.txt

Training data format:
Sentence, e.g. "我 想要 預約 耳鼻喉科" in source_sentence.txt
Slot, e.g. "o o o b-division" in source_slot.txt
Intent, e.g., "&3" in source_intent.txt
"""

import os
import csv
import ast
import jieba


def dfs(sen, depth, input_list, ans):
    if depth == len(input_list):
        ans.append(sen)
        return
    for j in input_list[depth]:
        sen += j
        dfs(sen, depth+1, input_list, ans)
        sen = sen[:-len(j)]


def data_generator(pattern_list):
    output = []
    dfs("", 0, pattern_list, output)
    return output


def disease_list_generator(disease_file, disease_list, division_list):
    for row in disease_file:
        for index, col in enumerate(row):
            if index == 0:  # Generate disease_list from disease_file
                disease_list.append(col + ' ')
                disease_list.append(col[0:len(col)-1] + ' ')
            elif index == 2:  # Generate division_list from disease_file
                for item in ast.literal_eval(col):
                    if division_list.count(item) == 0:
                        division_list.append(item + ' ')
                        if item[len(item)-2]=='科':
                            division_list.append(item[0:len(item)-1]+' ')
                        else:
                            division_list.append(item[0:len(item)-1]+'科'+' ')
                        if len(item)>3:
                            division_list.append(item[0:2]+'科'+' ')

def doctor_list_generator(division_file, doctor_list):
    for row in division_file:
        for index, col in enumerate(row):
            if index == 2:  # Generate doctor_list from division_file
                for item in ast.literal_eval(col):
                    if len(item) <= 3 and doctor_list.count(item) == 0:
                        doctor_list.append(item + ' ')
                        doctor_list.append(item[0] + '醫生' + ' ')
                        doctor_list.append(item[0] + '醫師' + ' ')

def main(data_dir):

    jieba.load_userdict("../data_resource/doctor_dict.txt")
    jieba.load_userdict("../data_resource/disease_dict.txt")
    jieba.load_userdict("../data_resource/division_dict.txt")
    jieba.load_userdict("../data_resource/other_dict.txt")

    div_rf = open("../data_resource/division.csv", "r")
    division_file = csv.reader(div_rf)
    dis_rf = open("../data_resource/disease.csv", "r")
    disease_file = csv.reader(dis_rf)

    disease_list = []
    division_list = []
    doctor_list = []
    time_list = ['星期一 ', '星期二 ', '星期三 ', '星期四 ', '星期五 ', '星期六 ', '星期日 ', '星期天 ',
                 '禮拜一 ', '禮拜二 ', '禮拜三 ', '禮拜四 ', '禮拜五 ', '禮拜六 ', '禮拜日 ', '禮拜天 ',
                 '明天 ', '後天 ', '今天 ']
    disease_list_generator(disease_file, disease_list, division_list)
    doctor_list_generator(division_file, doctor_list)

    disease_list_sample = ['青光眼']
    division_list_sample = ['外科']
    doctor_list_sample = ['王大明']
    time_list_sample = ['星期一']

    pattern_list = [
        [['嗨', '你好','妳好', '哈囉', '安安', 'hi', '嗨嗨', '早安', '午安', '晚安', '早上好', '勢早', 'Hello', 'hello','ㄤㄤ','早ㄤ'],['你好','您好','r',' ',''],[' ',''],[' ',' ',''],[' ',''], [' &0']],
        [['請問', ''], ['得', ''], disease_list_sample, ['會'], ['怎麼樣', '怎樣'], [' &1']],
        [['請問', ''], ['得', ''], disease_list_sample, ['會有'], ['什麼症狀', '哪些症狀'], [' &1']],
        [['我', ''], ['想', '要', '想要'], ['查', '查詢'], disease_list_sample, ['會有', '的'], ['症狀'] , [' &1']],
        [['我想知道', ''], ['得', ''], disease_list_sample, ['會有'], ['什麼症狀', '哪些症狀'], [' &1']],
        [['我想問', ''], ['得', ''], disease_list_sample, ['會'], ['怎麼樣', '怎樣'], [' &1']],


        [['我想知道','我想要問','我要問','想問','請問','如果', ''], ['得','有', ''], disease_list_sample, ['是', '屬於', '要看', '要掛', '要掛'], ['哪', '什麼','哪一','甚麼'], ['科','部'], [' &2']],
        [['我想知道','我想要問','我要問','想問','請問', ''], ['科別','部門'],[' ',''],[' ',''], [' &2']],

        [['請問', ''], ['星期一', ''], ['有', ''], ['什麼', '哪些'], ['醫生', '醫師'], ['可以'],
         ['看', '掛', '掛號', '預約'], disease_list_sample, ['的門診'], [' &3']],
        [['請問', ''], disease_list_sample, ['要', '可以'], ['看', '掛', '掛號', '預約'], ['什麼', '哪些'], ['醫生', '醫師'], [' &3']],

        [['請給我', '給我', '請告訴我', '告訴我', '請問',''], ['星期一', ''], disease_list_sample, ['的門診時刻表', '的門診時間','的時間'], [' &4']],
        [['請給我', '給我', '請告訴我', '告訴我', '請問',''], ['星期一', ''], division_list_sample, ['的門診時刻表', '的門診時間','的時間'], [' &4']],
        [['請給我', '給我', '請告訴我', '告訴我', '請問',''], ['星期一', ''], doctor_list_sample, ['的門診時刻表', '的門診時間','的時間','的看診時間'], [' &4']],
        [['我', ''], ['想', '要', '想要',''], ['問時間', '問門診時間', '知道時間'],[' ',''],[' ',' ',''], [' &4']],
        [['我', ''], ['想', '要', '想要',''],['知道','問'],doctor_list_sample, ['的時間', '的門診時間', '的看診時間'], [' &4']],

        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], ['星期一', ''], doctor_list_sample, ['的門診', ''], [' &5']],
        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], ['星期一', ''], division_list_sample, ['的門診', ''], [' &5']],
        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], ['星期一', ''], disease_list_sample, ['的門診'], [' &5']],
        [['我', ''], ['想', '要', '想要'], ['看', '掛', '掛號', '預約'], ['門診',''],[' &5']],
        
        [['謝謝', '掰掰','掰','okbye', '結束', '再見', 'bye', '好掰掰', '拜拜', '感謝', '好窩', '謝啦', '你真棒', '謝惹','再會','你可以走了'],[' ',' ',' ',''],[' ',' ',''],[' ',' ',''],[' ',' ',''],[' ',''],[' ',''], [' &6']]
    ]

    st_wf = open(os.path.join(data_dir, "source_sentence.txt"), "w")
    sl_wf = open(os.path.join(data_dir, "source_slot.txt"), "w")
    intent_wf = open(os.path.join(data_dir, "source_intent.txt"), "w")
    for lis in pattern_list:
        for sen in data_generator(lis):
            slot_tag = ""
            slot_parse = []
            seg_list = jieba.cut(sen.split()[0], cut_all=False)  # 精确模式
            for i, item in enumerate(seg_list):
                if i != 0:
                    slot_tag += " "
                if item in disease_list_sample:
                    slot_tag += 'b-disease'
                    slot_parse.append(disease_list)
                elif item in division_list_sample:
                    slot_tag += 'b-division'
                    slot_parse.append(division_list)
                elif item in doctor_list_sample:
                    slot_tag += 'b-doctor'
                    slot_parse.append(doctor_list)
                elif item in time_list_sample:
                    slot_tag += 'b-time'
                    slot_parse.append(time_list)
                else:
                    slot_tag += 'o'
                    li = []
                    li.append(item + ' ')
                    slot_parse.append(li)
            for slot_sen in data_generator(slot_parse):
                #modify_sen = slot_sen[:len(slot_sen)-1]
                #output_sen = modify_sen
                output_sen = slot_sen[:len(slot_sen)-1]
                output_intent = sen.split()[1]
                output_slot = slot_tag
                print(output_sen, file=st_wf)
                print(output_slot, file=sl_wf)
                print(output_intent, file=intent_wf)

    div_rf.close()
    dis_rf.close()
    st_wf.close()
    sl_wf.close()
    intent_wf.close()

if __name__ == '__main__':
    #data_dir = "data/hospital"
    main(data_dir)

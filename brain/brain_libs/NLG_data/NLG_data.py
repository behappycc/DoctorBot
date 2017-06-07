"""
Usage:
python3 NLG_data.py

Output:
data.json
"""
import csv
import ast


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
                disease_list.append(col)
            elif index == 2:  # Generate division_list from disease_file
                for item in ast.literal_eval(col):
                    if division_list.count(item) == 0:
                        division_list.append(item)


def doctor_list_generator(division_file, doctor_list):
    for row in division_file:
        for index, col in enumerate(row):
            if index == 2:  # Generate doctor_list from division_file
                for item in ast.literal_eval(col):
                    if len(item) <= 3 and doctor_list.count(item) == 0:
                        doctor_list.append(item)


def search_disease_file(file, disease_name, column):
    for row in file:
        if row[0] == disease_name:
            return ",".join(ast.literal_eval(row[column]))
    return ""


def search_doctor(file, disease_name, division_name):
    for row in file:
        if disease_name != "":
            if disease_name in row[1]:
                return ",".join(ast.literal_eval(row[2]))
        elif division_name != "":
            if division_name in row[0]:
                return ",".join(ast.literal_eval(row[2]))
    return ""


def main():

    div_rf = open("division.csv", "r",encoding='utf-8')
    division_file = csv.reader(div_rf)
    dis_rf = open("disease.csv", "r",encoding='utf-8')
    disease_file = csv.reader(dis_rf)
    disease_list = []
    division_list = []
    doctor_list = []
    disease_list_generator(disease_file, disease_list, division_list)
    doctor_list_generator(division_file, doctor_list)
    div_rf.close()
    dis_rf.close()
    slot_list = ['intent', 'disease', 'division', 'doctor', 'time']
    intent_list = ['查詢症狀', '查詢科別', '查詢醫生', '查詢時刻表', '掛號']

    json_list = []
#inform
    inform_list = [
        ["inform(slot='intent')","請問你要做什麼","請告訴我您需要什麼協助"],
        ["inform(slot='disease')","請問疾病的名稱","請告訴我疾病的名稱"],
        ["inform(slot='division')","請問是哪個科別","請告訴我科別名稱"],
        ["inform(slot='doctor')","請問要哪位醫生","請告訴我醫生名稱"],
        ["inform(slot='time')","請問要哪天","請告訴我時間"]
    ]
    for item in inform_list:
        json_list.append(item)
#select
    select_intent = ['查詢症狀,查詢科別', '查詢症狀,查詢醫生', '查詢症狀,查詢時刻表', '查詢症狀,掛號',
                     '查詢科別,查詢醫生', '查詢科別,查詢時刻表', '查詢科別,掛號',
                     '查詢醫生,查詢時刻表', '查詢時刻表,掛號', '查詢醫生掛號']
    item = []
    for intent in select_intent:
        item.append("select(slot='intent',intent='" + intent + "'")
        item.append("請選擇服務項目," + intent)
        item.append("請問您想要哪個服務," + intent)
        json_list.append(item)
        item = []

    select_disease = []
    for index, item in enumerate(disease_list):
        if 2 < index < len(disease_list)-2:
            select_disease.append(item + "," + disease_list[index+1])
    item = []
    for dis in select_disease:
        item.append("select(slot='disease',disease='" + dis + "'")
        item.append("請選擇疾病名稱," + dis)
        item.append("請問是哪一個疾病," + dis)
        json_list.append(item)
        item = []

    select_division = []
    for index, item in enumerate(division_list):
        if 2 < index < len(division_list)-2:
            select_division.append(item + "," + division_list[index+1])
    item = []
    for dis in select_division:
        item.append("select(slot='division',division='" + dis + "'")
        item.append("請選擇科別," + dis)
        item.append("請問您要選擇哪個科別," + dis)
        json_list.append(item)
        item = []

    select_doctor = []
    for index, item in enumerate(doctor_list):
        if 2 < index < len(doctor_list)-2:
            select_doctor.append(item + "," + doctor_list[index+1])
    item = []
    for dis in select_division:
        item.append("select(slot='division',division='" + dis + "'")
        item.append("請選擇醫生," + dis)
        item.append("請問您要選擇哪位醫生," + dis)
        json_list.append(item)
        item = []

    select_time = ['106.5.5,106.5.6','106.5.4,106.1.6','106.5.25,106.5.16','106.2.5,106.5.4',
                   '107.5.5,106.5.6','106.9.5,106.5.6','106.5.20,106.7.6','106.5.4,106.3.6']
    item = []
    for dis in select_time:
        item.append("select(slot='time',time='" + dis + "'")
        item.append("請選擇日期," + dis)
        item.append("請問您要哪天," + dis)
        json_list.append(item)
        item = []
#confirm
    item = []
    for intent in intent_list:

        item.append("confirm(slot='intent',intent='" + intent + "'")
        item.append("請問您是要" + intent + "對嗎？")
        item.append("是不是要" + intent)
        json_list.append(item)
        item = []

    item = []
    for dis in disease_list:
        item.append("confirm(slot='disease',disease='" + dis + "'")
        item.append("請問您是說" + dis + "對嗎？")
        item.append("是" + dis + "嗎？")
        json_list.append(item)
        item = []

    item = []
    for dis in division_list:
        item.append("confirm(slot='division',division='" + dis + "'")
        item.append("請問您是說" + dis + "對嗎？")
        item.append("是" + dis + "嗎？")
        json_list.append(item)
        item = []

    item = []
    for dis in doctor_list:
        item.append("confirm(slot='doctor',doctor='" + dis + "'")
        item.append("請問您是說" + dis + "醫生嗎？")
        item.append("是" + dis + "醫生嗎？")
        json_list.append(item)
        item = []

    select_time = ['106.5.5','106.5.4','106.1.6','106.5.25','106.5.16','106.2.5','106.5.4',
                   '107.5.5','106.5.6','106.9.5','106.5.6','106.5.20','106.7.6','106.5.4','106.3.6']
    item = []
    for dis in select_time:
        item.append("confirm(slot='time',time='" + dis + "'")
        item.append("請問您是說" + dis + "這天嗎？")
        item.append("是" + dis + "對嗎？")
        json_list.append(item)
        item = []

    dis_rf = open("disease.csv", "r",encoding='utf-8')
    disease_file = csv.reader(dis_rf)
#End
    item = []
    for dis in disease_list:
        result = search_disease_file(disease_file, dis, 4)
        if result != "":
            item.append("end(intent='1',disease='" + dis + "',results='" + result + "'")
            item.append("已經幫您查詢症狀,以下是" + dis + "的症狀," + result)
            item.append(dis + "的症狀有" + result)
            json_list.append(item)
            item = []
    dis_rf.close()

    dis_rf = open("disease.csv", "r",encoding='utf-8')
    disease_file = csv.reader(dis_rf)
    item = []
    for dis in disease_list:
        result = search_disease_file(disease_file, dis, 2)
        if result != "":
            item.append("end(intent='2',disease='" + dis + "',results='" + result + "'")
            item.append("已經幫您查詢科別," + dis + "的科別是," + result)
            item.append(dis + "的相關科別是" + result)
            json_list.append(item)
            item = []
    dis_rf.close()

    div_rf = open("division.csv", "r",encoding='utf-8')
    division_file = csv.reader(div_rf)
    item = []
    for dis in disease_list:
        result = search_doctor(division_file, dis, "")
        if result != "":
            item.append("end(intent='3',disease='" + dis + "',results='" + result + "'")
            item.append("已經幫您查詢到" + dis + "的主治醫生有," + result)
            item.append(dis + "的主治醫師有" + result)
            json_list.append(item)
            item = []
    div_rf.close()

    div_rf = open("division.csv", "r",encoding='utf-8')
    division_file = csv.reader(div_rf)
    item = []
    for dis in disease_list:
        result = search_doctor(division_file, dis, "")
        if result != "":
            item.append("end(intent='3',division='眼科',results='" + result + "'")
            item.append("已經幫您查詢到眼科的主治醫生有," + result)
            item.append("眼科的主治醫師有" + result)
            json_list.append(item)
            item = []
    div_rf.close()

    item = []
    for dis in disease_list:
        item.append("end(intent='4',disease='" + dis + "',doctor='胡芳蓉',results='106.5.5,106.5.6'")
        item.append("已經幫您查詢到" + dis + "胡芳蓉醫師的門診時刻有106.5.5,106.5.6,")
        item.append(dis + "胡芳蓉醫師的門診時刻有106.5.5,106.5.6")
        json_list.append(item)
        item = []

    item = []
    for dis in division_list:
        item.append("end(intent='4',division='" + dis + "',doctor='胡芳蓉',results='106.5.5,106.5.6'")
        item.append("已經幫您查詢到" + dis + "胡芳蓉醫師的門診時刻有106.5.5,106.5.6,")
        item.append(dis + "胡芳蓉醫師的門診時刻有106.5.5,106.5.6")
        json_list.append(item)
        item = []

    item = []
    for dis in disease_list:
        item.append("end(intent='5',disease='" + dis + "',doctor='胡芳蓉',time='106.5.5'")
        item.append("已經幫您掛號" + dis + "胡芳蓉醫師106.5.5的門診")
        item.append(dis + "胡芳蓉醫師106.5.5的門診已掛號完成")
        json_list.append(item)
        item = []

    item = []
    for dis in division_list:
        item.append("end(intent='5',division='" + dis + "',doctor='胡芳蓉',time='106.5.5'")
        item.append("已經幫您掛號" + dis + "胡芳蓉醫師106.5.5的門診")
        item.append(dis + "胡芳蓉醫師106.5.5的門診已掛號完成")
        json_list.append(item)
        item = []

    data_write = open("data.json", "w",encoding='utf-8')
    print(json_list, file=data_write)
    #for list_item in json_list:
    #    print(list_item)
    print("created " + str(len(json_list)) + " data")
    data_write.close()

if __name__ == '__main__':
    main()
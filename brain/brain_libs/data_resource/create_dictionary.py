"""

Usage:
python3 create_dictionary.py
**Please put disease.csv and division.csv in the same folder

Output:
doctorbot_dict.txt

"""
import csv
import ast


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


def main():

    div_rf = open("division.csv", "r")
    division_file = csv.reader(div_rf)
    dis_rf = open("disease.csv", "r")
    disease_file = csv.reader(dis_rf)
    disease_list = []
    division_list = []
    doctor_list = []
    disease_list_generator(disease_file, disease_list, division_list)
    doctor_list_generator(division_file, doctor_list)

    doc_f = open("doctor_dict.txt", "w")
    dis_f = open("disease_dict.txt", "w")
    div_f = open("division_dict.txt", "w")
    o_f = open("other_dict.txt", "w")
    print('請問', file=o_f)
    for word in disease_list:
        print(word, file=dis_f)
    for word in division_list:
        print(word, file=div_f)
    for word in doctor_list:
        print(word, file=doc_f)

    div_rf.close()
    dis_rf.close()
    doc_f.close()
    dis_f.close()
    div_f.close()
    o_f.close()

if __name__ == '__main__':
    main()


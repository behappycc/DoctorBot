"""

Usage:
python3 create_dictionary.py
**Please put disease.csv and division.csv in the same folder

Output:
doctorbot_dict.txt

"""
import csv
import ast


def merge_table(disease_file, division_file):
    csv_list = []
    dis_lis = []
    for dis_row in disease_file:
        disease_name = dis_row[0]
        for div_row in division_file:
            for dis_item in ast.literal_eval(div_row[1]):
                if disease_name in dis_item and disease_name not in dis_lis:
                    dis_lis.append(disease_name)
                    new_row = []
                    for index, dis_col in enumerate(dis_row):
                        if index == 2:
                            new_row.append(div_row[0])
                        else:
                            new_row.append(dis_col)
                    new_row.append(div_row[2])
                    csv_list.append(new_row)
    return csv_list


def main():

    with open('division.csv', 'r') as div_rf:
        reader = csv.reader(div_rf)
        division_list = list(reader)
    with open('disease.csv', 'r') as dis_rf:
        reader = csv.reader(dis_rf)
        disease_list = list(reader)

    table = merge_table(disease_list, division_list)
    with open("merge.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(table)
    f.close()
    div_rf.close()
    dis_rf.close()


if __name__ == '__main__':
    main()


import csv
import numpy as np
def log_reader():
with open('example_dialogue.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        count = 1
        r1 = 1002
        s_t = []
        r_t = []
        all_training = []
        for row in spamreader:
            if count%5 == 1 :
                s_t1 = row[0].split(',')
                s_t1 = list(map(float,s_t1))
                s_t1 = list(map(int,s_t1))
                if r1 !=1002 :
                     all_training.append([s_t,a_t,r1,s_t1,terminal])
            if count%5 == 2:
                s_t = row[0].split(',')
                s_t = list(map(float,s_t))
                s_t = list(map(int,s_t))

            if count%5 == 3: 
                a_t = row[0].split(',')
                a_t = list(map(float,a_t))
                a_t = list(map(int,a_t))
    #            print(a_t)
            if count%5 == 4: 
                r1 = int(row[0])
            if count%5 == 0: 
                if row[0] =='True':
                    terminal = True
                else:
                    terminal = False

            count = count+1
        print(all_training)
        return all_training

    csvfile.close()
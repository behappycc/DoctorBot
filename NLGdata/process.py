import csv
with open('NLGdata.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    table = [row for row in reader]

with open('greeting.txt','w') as f:
    for row in table:
        f.write(row['1. 打招呼']+ '\n')

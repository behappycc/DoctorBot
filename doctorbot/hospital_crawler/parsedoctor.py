import csv
c = 0
fs= []
ss= [] 
ts = []
inin = []
f = open('division.csv', 'r')
res = []
for row in csv.reader(f):
	i = False
	temp = "".join(row)
	if(temp.find('部')!=-1 or temp.find('中心')!=-1 or temp.find('醫院')!=-1):
		inin = [fs,ss,ts]
		if(ts!=[]):
			res.append(inin)
		fs= []
		ss= [] 
		ts = []
		inin = []
		if(temp.find('部')!=-1):
			a = temp.index('部')
		elif(temp.find('中心')!=-1):
			a = temp.index('心')
		else:
			a = temp.index('院')
		fs = temp[0:a+1]
		if(temp.find('專')!=-1):	
			b = temp.index('專')
			ss = temp[a+1:b]
			ts = temp[b:]
	else:
		tempts = [ts,temp]
		ts = "".join(ts)
inin = [fs,ss,ts.split("、")]
res.append(inin)
	
"""for i in range(len(temp)):
	a = temp.split('部',1)
	b = a.split('專',1)
	c = temp[2]
	print(b)
	for i in range(len(row)):
		print(i) 
		if(i == len(row)):
			res.append("".join(temp))
		elif(i>2):
			temp.append(row[i])
		else:
			res.append(row[i])
"""
a = open("parse.csv","w")
w= csv.writer(a)
w.writerows(res)
f.close()


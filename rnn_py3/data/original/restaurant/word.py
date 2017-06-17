import json
import re

def word2id(file):
	word = {}
	
	wordlist = []
	with open(file+'.json','r',encoding='utf-8') as f:
		ff = json.load(f)
	for lines in ff[0:]:
		for words in lines:
			for word in words:
				if word not in wordlist	:
					wordlist.append(word)

	wordlist = list(re.sub(r'[a-zA-z0-9()=,;\'\"]','',str(wordlist)).split())
	word = dict(enumerate(wordlist))
	print(word)

	with open(file+'_id.txt','w',encoding='utf-8') as f:
		f.write(str(word))


def main():
	word2id('train')
	word2id	('test')
	word2id('valid')

if __name__ =='__main__':
	main()
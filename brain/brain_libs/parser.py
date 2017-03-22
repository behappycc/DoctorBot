import jieba
jieba.load_userdict("doctorbot_dict.txt")

stop_words = [' ', '\n']
sentences = []
with open('dialogue.txt', 'r') as file:
    for line in file:
        print (line)
        sentence = []  
        for word in jieba.cut(line):
            if word not in stop_words:
                sentence.append(word)
        sentences.append(sentence)
print (sentences)
import jieba
import numpy as np
jieba.load_userdict("doctorbot_dict.txt")


class SyntaxAnalysis(object):
    def __init__(self):
        pass

    def segment_words(self):
        stop_words = [' ', '\n']
        sentences = []
        with open('dialogue.txt', 'r', encoding="utf-8") as file:
            for line in file:
                print (line)
                sentence = []
                for word in jieba.cut(line):
                    if word not in stop_words:
                        sentence.append(word)
                sentences.append(sentence)
        print (sentences)
        return sentences

    def generate_corpus(self, words):
        corpus_dict = {}
        corpus_list = []
        for word in words:
            if word in corpus_dict:
                corpus_dict[word] += 1
            else:
                corpus_dict[word] = 1
        print(corpus_dict)

        for key, value in corpus_dict.items():
            corpus_list.append(key)
        print (corpus_list)
        return corpus_list

    def one_hot_encode(self, corpus_list, sentence_words):
        for s_word in sentence_words:
            one_hot_list = np.zeros(len(corpus_list) + 1)
            if s_word not in corpus_list:
                one_hot_list[-1] = 1
                print('word: {} one-hot: {}'.format(s_word, one_hot_list))
            else:
                for index, word in enumerate(corpus_list):
                    if word == s_word:
                        one_hot_list[index] = 1
                        print('word: {} one-hot: {}'.format(s_word, one_hot_list))


def main():
    sa = SyntaxAnalysis()
    sa.segment_words()
    words = ['妳好', '妳好', '妳好', '妳', '好']
    sentence_words = ['妳好', '妳', '好', '哈']
    corpus_list = sa.generate_corpus(words)
    sa.one_hot_encode(corpus_list, sentence_words)


if __name__ == '__main__':
    main()

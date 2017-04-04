from generate_vector import generate_vector
import numpy as np
import json
from keras.models import load_model
from keras.models import model_from_json
loaded_model = load_model('intent_model.h5')

sentence = input('yout sentence: ')
print (sentence)
gv = generate_vector()
sentences, maxsize = gv.segment_words(sentence)
print ("senteces size: {}".format(np.shape(sentences)))

with open('dict_one_hot_word.txt', 'r', encoding='utf-8') as f:
    dict_one_hot_word = json.load(f)

one_hot_words = gv.one_hot_encode(1467, sentences, maxsize, dict_one_hot_word)
print (one_hot_words.shape)
one_hot_words = one_hot_words.reshape(-1,15,1468)

print ('intent is {}'.format(loaded_model.predict_classes(one_hot_words)))
import numpy as np

vocab_file = '../resource/vocab'
vector_file = 'vectors_custom-80.txt'
dim = 80
with open(vector_file, mode='w') as fout:
    with open(vocab_file, mode='r') as fin:
        for line in fin.readlines():
            #w2vec.append(line+str(np.zeros(dim, dtype=float)))
            fout.write(line.replace('\n','')+str(np.zeros(dim, dtype=float)[:])\
                       .replace('[','').replace(']','').replace('\n',''))
            fout.write('\n')

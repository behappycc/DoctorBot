######################################################################
######################################################################
#  Copyright Tsung-Hsien Wen, Cambridge Dialogue Systems Group, 2016 #
######################################################################
######################################################################
import os
import sys
import operator
sys.path.append('./utils/')
import itertools
import nltk
import json
import re


class DataLexicaliser(object):

    def __init__(self):
        fin = open('resource/special_values.txt')
        self.special_values= list(json.load(fin).keys()) + ['?']
        fin.close()
        fin = open('resource/special_slots.txt')
        self.special_slots = json.load(fin)
        fin.close()

    def delexicalise(self,sent,jssv):
        raise NotImplementedError('method delexicalise() hasn\'t been implemented')
    def lexicalise(self,sent,jssv):
        raise NotImplementedError('method lexicalise() hasn\'t been implemented')

class ExactMatchDataLexicaliser(DataLexicaliser):

    def __init__(self):
        DataLexicaliser.__init__(self)
        self.typetoken = ''

    def delexicalise(self,sent,jssv):
        # no slot values return directly
        if len(jssv)==1 and jssv[0][1]==None:
            return sent
        #print('be_jssv: '+str(jssv))
        #print('be_sent: '+sent)
        for slot,value in sorted(jssv,key=lambda x:len(x[-1]),reverse=True):
            #print('slot: '+slot)
            #print('value: '+value)
            if  value in self.special_values : continue # special values, skip

            # taking care of all possible permutations of multiple values
            #print('before: '+value)
            #vs = value.replace(' or ',' and ').split(' and ')
            vs = value.split(',')
            #print('after: '+str(vs))
            #permutations =  [' and '.join(x) for x in itertools.permutations(vs)]+\
            #                [' or '.join(x) for x in itertools.permutations(vs)]
            permutations =  [' , '.join(x) for x in itertools.permutations(vs)]

            #permutations = permutations.split(',')
            #print(permutations)
            # try to match for each possible permutation
            isMatched = False
            for p in permutations:
                p = re.sub('\d{3}\.\d\.\d', '99999', p) # time_slot
                #print(sent)
                if p in sent : # exact match , ends
                    sent = (' '+sent+' ').replace(\
                            ' '+p+' ',' SLOT_'+slot.upper()+' ',1)[1:-1]
                    isMatched = True
                    break
            if not isMatched:
                pass
                #raise ValueError('value "'+value+'" cannot be delexicalised!')

        #print(sent)
        return sent

    def lexicalise(self,sent,jssv):
        # no slot values return directly
        if len(jssv)==1 and jssv[0][1]==None:
            return sent

        # replace values
        for slot,value in sorted(jssv,key=lambda x:len(x[0]),reverse=True):
            if  value in self.special_values : continue # special values, skip
            if 'SLOT_'+slot.upper() not in sent :
                pass
                #raise ValueError('slot "SLOT_'+slot.upper()+'" does not exist !')
            else:
                sent=(' '+sent+' ').replace(' SLOT_'+slot.upper()+' ',' '+value+' ',1)[1:-1]
        sent = (' '+sent+' ').replace(' SLOT_TYPE ',' '+self.typetoken+' ')[1:-1]
        #print(sent)
        return sent


#if __name__ == '__main__':


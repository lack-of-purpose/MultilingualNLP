#!/usr/bin/env python3
#coding: utf-8

import sys

# field indexes
ID = 0
FORM = 1
LEMMA = 2
UPOS = 3
XPOS = 4
FEATS = 5
HEAD = 6
DEPREL = 7
    
for line in sys.stdin:
    fields = line.strip().split('\t')
    if len(fields) >= 1 and fields[ID].isdigit():
        # TODO harmonize the tag, store the harmonized tag into UPOS
        
        if fields[XPOS].startswith('NN'):
            fields[UPOS] = 'NOUN' 
        elif fields[XPOS].startswith('Vc'):
            fields[UPOS] = 'PART'
        elif fields[XPOS].startswith('V'):
            fields[UPOS] = 'VERB'
        elif fields[XPOS].startswith('J^'):
            fields[UPOS] = 'CCONJ'
        elif fields[XPOS].startswith('J,'):
            fields[UPOS] = 'SCONJ'
        elif fields[XPOS].startswith('AA'):
            fields[UPOS] = 'ADJ'
        elif fields[XPOS].startswith('Z'):
            fields[UPOS] = 'PUNCT'
        elif fields[XPOS].startswith('R'):
            fields[UPOS] = 'ADP'
        elif fields[XPOS].startswith('Dg'):
            fields[UPOS] = 'ADV'
        elif fields[XPOS].startswith('Db'):
            fields[UPOS] = 'ADV'
        elif fields[XPOS].startswith('P7'):
            fields[UPOS] = 'PART'
        elif fields[XPOS].startswith('P'):
            fields[UPOS] = 'PRON'
        elif fields[XPOS].startswith('C'):
            fields[UPOS] = 'NUM'
        elif fields[XPOS].startswith('T'):
            fields[UPOS] = 'PART'
        else:
            fields[UPOS] = fields[XPOS]

        # output
        print('\t'.join(fields))
    else:
        # pass thru
        print(line.strip())


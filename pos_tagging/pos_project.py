#!/usr/bin/env python3
#coding: utf-8

import sys
from collections import defaultdict
import random

# parameters
#conllu, conllu, alignment
source_filename, target_filename, alignment_filename = sys.argv[1:4]

# number of sentences -- in PUD it is always 1000
SENTENCES = 60035

# field indexes
ID = 0
FORM = 1
LEMMA = 2
UPOS = 3
XPOS = 4
FEATS = 5
HEAD = 6
DEPREL = 7

random.seed(13)
# returns dict[source_id] = [target_id_1, target_id_2, target_id_3...]
# and a reverse one as well
# TODO depending on what type of alignment you use, you may not need to have a list of aligned tokens -- maybe there is at most one, or even exactly one?
def read_alignment(fh):
    line = fh.readline()
    src2tgt = defaultdict(list)
    tgt2src = defaultdict(list)
    for st in line.split():
        (src, tgt) = st.split('-')
        src = int(src)
        tgt = int(tgt)
        src2tgt[src].append(tgt)
        tgt2src[tgt].append(src)
    return (src2tgt, tgt2src)

# returns a list of tokens, where each token is a list of fields;
# ID and HEAD are covnerted to integers and switched from 1-based to 0-based
# if delete_pos=True, then morphological anotation (UPOS, XPOS, FEATS) is stripped
def read_sentence(fh, delete_pos=False):
    sentence = list()
    for line in fh:
        if line == '\n':
            # end of sentence
            break
        elif line.startswith('#'):
            # ignore comments
            continue
        else:
            fields = line.strip().split('\t')
            if fields[ID].isdigit():
                # make IDs 0-based to match alignment IDs
                fields[ID] = int(fields[ID])-1
                # fields[HEAD] = int(fields[HEAD])-1
                if delete_pos:
                    fields[UPOS] = '_'
                    fields[XPOS] = '_'
                    fields[FEATS] = '_'
                sentence.append(fields)
            # else special token -- continue
    return sentence

# takes list of lists as input, ie as returned by read_sentence()
# switches ID and HEAD back to 1-based and converts them to strings
# joins fields by tabs and tokens by endlines and returns the CONLL string
def write_sentence(sentence):
    result = list()
    for fields in sentence:
        # switch back to 1-based IDs
        fields[ID] = str(fields[ID]+1)
        # fields[HEAD] = str(fields[HEAD]+1)
        result.append('\t'.join(fields))
    result.append('')
    return '\n'.join(result)

with open(source_filename, encoding="utf8") as source, open(target_filename, encoding="utf8") as target, open(alignment_filename) as alignment:
    upos_count = {}
    word_upos_bi_count = {}
    for sentence_id in range(SENTENCES):
        (src2tgt, tgt2src) = read_alignment(alignment)
        source_sentence = read_sentence(source)
        target_sentence = read_sentence(target, delete_pos=True)
        
        for key in src2tgt.keys():
            if source_sentence[key][UPOS] in upos_count.keys():
                upos_count[source_sentence[key][UPOS]] += 1
            else:
               upos_count[source_sentence[key][UPOS]] = 1
                        
    sum_values = sum(upos_count.values())
    upos_probs = []
    upos_tags = []
    for key in upos_count.keys():
        upos_probs.append(upos_count[key]/sum_values)
        upos_tags.append(key)
         
with open(source_filename, encoding="utf8") as source, open(target_filename, encoding="utf8") as target, open(alignment_filename) as alignment, open('output.conllu', 'w', encoding="utf8") as out:         
    for sentence_id in range(SENTENCES):
        (src2tgt, tgt2src) = read_alignment(alignment)
        source_sentence = read_sentence(source)
        target_sentence = read_sentence(target, delete_pos=True)
        
        # TODO do the projection
        # iterate over source tokens
        # TODO maybe you want to iterate over target tokens?
        for source_token in source_sentence:
            source_token_id = source_token[ID]
            # for each target token aligned to source_token (if any)
            for target_token_id in src2tgt[source_token_id]:
                # pass
                # TODO copy source UPOS to target UPOS?
                target_sentence[target_token_id][UPOS] = source_sentence[source_token_id][UPOS]
                
        for word in target_sentence:
            if word[UPOS] == '_':
                tag = random.choices(upos_tags, weights=upos_probs, k=1)
                word[UPOS] = tag[0]
        #print(write_sentence(target_sentence))
        res = write_sentence(target_sentence)
        out.write(f'# sent_id = {sentence_id+1}\n')
        out.write(res)
        out.write('\n')

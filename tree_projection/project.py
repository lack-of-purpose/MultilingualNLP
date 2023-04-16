#!/usr/bin/env python3
#coding: utf-8

import sys
from collections import defaultdict

# parameters
source_filename, target_filename, alignment_filename = sys.argv[1:4]

# number of sentences -- in PUD it is always 1000
SENTENCES = 1000

# field indexes
ID = 0
FORM = 1
LEMMA = 2
UPOS = 3
XPOS = 4
FEATS = 5
HEAD = 6
DEPREL = 7

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
# if delete_tree=True, then syntactic anotation (HEAD and DEPREL) is stripped
def read_sentence(fh, delete_tree=False):
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
                fields[HEAD] = int(fields[HEAD])-1
                if delete_tree:
                    # reasonable defaults:
                    fields[HEAD] = -1       # head = root
                    fields[DEPREL] = 'dep'  # generic deprel
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
        fields[HEAD] = str(fields[HEAD]+1)
        result.append('\t'.join(fields))
    result.append('')
    return '\n'.join(result)

### fill the deprels based on UPOS
def dep_from_upos(upos):
    dep = 'dep'
    if upos == 'PUNCT' or upos == 'SYM':
        dep = 'punct'
    elif upos == 'NOUN':
        dep = 'obj'
    elif upos == 'AUX':
        dep = 'aux'
    elif upos == 'DET':
        dep = 'det'
    elif upos == 'NUM':
        dep = 'nummod'
    elif upos == 'ADP':
        dep = 'case'
    elif upos == 'CCONJ':
        dep = 'conj'
    elif upos == 'ADV':
        dep = 'advmod'
    
    return dep

with open(source_filename, encoding="utf8") as source, open(target_filename, encoding="utf8") as target, open(alignment_filename) as alignment, open('output.conllu', 'w', encoding="utf8") as out:
    for sentence_id in range(SENTENCES):
        (src2tgt, tgt2src) = read_alignment(alignment)
        source_sentence = read_sentence(source)
        target_sentence = read_sentence(target, delete_tree=True)
        
        head_dep = {}
        root = 0
        for source_token in source_sentence:
            if source_token[DEPREL] == 'root':
                root = source_token[ID]
                continue
            if source_token[HEAD] in head_dep.keys():
                head_dep[source_token[HEAD]].append(source_token[ID])
            else:
                head_dep[source_token[HEAD]] = [source_token[ID]]

        for head in head_dep.keys():
            trg_head = -1
            ### choosing head in target
            if len(src2tgt[head]) > 1:
                for trg_token in src2tgt[head]:
                    if target_sentence[trg_token][UPOS] == source_sentence[head][UPOS]:
                        trg_head = trg_token
                if trg_head == -1:
                    trg_head = src2tgt[head][0]
                for trg_token in src2tgt[head]:
                    if trg_token != trg_head:
                        target_sentence[trg_token][HEAD] = trg_head
                        dep = dep_from_upos(target_sentence[trg_token][UPOS])
                        if dep != 'dep':
                            target_sentence[trg_token][DEPREL] = dep
                        else:
                            target_sentence[trg_token][DEPREL] = source_sentence[head][DEPREL]
            elif len(src2tgt[head]) == 1:
                trg_head = src2tgt[head][0]
                if source_sentence[head][DEPREL] == 'root':
                    target_sentence[trg_head][HEAD] = -1
                    target_sentence[trg_head][DEPREL] = 'root'
            else:
                continue
            ### adding dependencies
            for dep in head_dep[head]:
                for token_id in src2tgt[dep]:
                    if target_sentence[token_id][HEAD] == -1:
                        target_sentence[token_id][HEAD] = trg_head
                        target_sentence[token_id][DEPREL] = source_sentence[dep][DEPREL]
        
        ### fill the default deprels using UPOS
        for target_token in target_sentence:
            if target_token[DEPREL] == 'dep':
                dep = dep_from_upos(target_token[UPOS])
                target_token[DEPREL] = dep
                
        ### get all heads from the sentence
        heads = []
        for target_token in target_sentence:
            if target_token[HEAD] != -1:
                heads.append(target_token[HEAD])

        ### check root
        roots = {}
        ### get all roots from the sentence
        for target_token in target_sentence:
            if target_token[HEAD] == -1 and target_token[DEPREL] == 'root':
                if target_token[ID] in roots.keys():
                    roots[target_token[ID]] += 1
                else:
                    roots[target_token[ID]] = 1
        ### if there is more than 1 root - one of them with the most amount of deps become the root
        if len(roots.keys()) > 1:
            root = max(roots, key=roots.get)
            for k in roots.keys():
                if k != root:
                    target_sentence[k][HEAD] = root
        
        ### if no roots - the head with the most amount of deps become the root
        if len(roots.keys()) == 0:
            root = max(set(heads), key=heads.count)
            target_sentence[root][HEAD] = -1
            target_sentence[root][DEPREL] = 'root'
            roots[root] = 1
        
        ### if exactly one root - save it
        if len(roots.keys()) == 1:
            for k in roots.keys():
                root = k

        ### for unassigned nodes - set the root as their head
        for target_token in target_sentence:
            if  target_token[HEAD] == -1 and target_token[DEPREL] != 'root':
                target_token[HEAD] = root
        
        ### check cycles - if there is one, destroy it by redirecting the cycling node to the root
        branch = []
        for target_token in target_sentence:
            branch.append(target_token[ID])
            current_node = target_sentence[target_token[HEAD]]
            while len(branch) == len(set(branch)) and current_node[HEAD] != 0:
                branch.append(current_node[ID])
                current_node = target_sentence[current_node[HEAD]]
            
            if len(branch) != len(set(branch)):
                target_sentence[branch[-2]][HEAD] = root
                
            branch = []
        
        res = write_sentence(target_sentence)
        out.write(f'# sent_id = {sentence_id+1}\n')
        out.write(res)
        out.write('\n')

import pandas as pd
import numpy as np
import json

languages = pd.read_csv('data/languages.csv')
values = pd.read_csv('data/values.csv')

lang_genus = languages[['ID', 'Genus']]  #languages and genera
lang_id_value = values[['Language_ID', 'Parameter_ID', 'Value']] #languages, features and their values

params = lang_id_value['Parameter_ID'].unique() #features
params.sort()

langs = lang_id_value['Language_ID'].unique() #languages

num_of_features = len(params)
num_of_languages = len(langs)

values = list(range(0,num_of_features))
features_dict = {params[i]: values[i] for i in range(len(params))} #dictionary feature : column_num

values = list(range(0,num_of_languages))
langs_dict = {langs[i]: values[i] for i in range(len(langs))} #dictionary language : row_num

with open('data/languages.txt', 'w') as languages:
     languages.write(json.dumps(langs_dict))
     
keys = list(lang_genus['ID'])
values = list(lang_genus['Genus'])
lang_genus_dict = {keys[i]: values[i] for i in range(len(keys))} #dictionary language : genus

with open('data/genus.txt', 'w') as genus:
     genus.write(json.dumps(lang_genus_dict))

     
''' Create the numpy array language x features'''
param_value_np = np.zeros((num_of_languages, num_of_features))
param_value_np[:] = np.nan
list_of_langs = langs.tolist()
i = 0
for language in list_of_langs:
    np_row = [np.nan] * num_of_features
    temp = lang_id_value[lang_id_value['Language_ID'] == language]
    param_value = temp[['Parameter_ID', 'Value']]
    keys = list(param_value['Parameter_ID'])
    values = list(param_value['Value'])
    param_value_dict = {keys[i]: values[i] for i in range(len(keys))}
    for key in param_value_dict.keys():
        pos = features_dict[key]
        np_row[pos] = param_value_dict[key]
    param_value_np[i,:] = np_row
    i += 1

np.savetxt('data/param_value.csv', param_value_np, delimiter=',')
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--genus", default='Slavic', type=str, help="Genus")


def main(args: argparse.Namespace):
    par_val = np.loadtxt('data/param_value.csv', delimiter=',') # feature_value
    with open('test/languages.txt') as f:
        languages = f.read()
    langs_dict = json.loads(languages)

    with open('test/genus.txt') as f:
        genus = f.read()
    lang_genus_dict = json.loads(genus)

    genus = args.genus

    languages_in_genus = []

    for lang in lang_genus_dict.keys():
        if lang_genus_dict[lang] == genus:
            languages_in_genus.append(lang)

    centroid = ''
    centr_score = -1
    dissim_score = 100
    weirdest = ''
    lang_score_dict = {}
    for lang in languages_in_genus:
        score = 0
        lang_row = langs_dict[lang]
        for another_lang in languages_in_genus:
            if another_lang == lang:
                continue
            another_lang_row = langs_dict[another_lang]
            num_of_common_features = np.count_nonzero(~np.isnan(par_val[lang_row,:] + par_val[another_lang_row,:]))
            compare = (par_val[lang_row,:] == par_val[another_lang_row,:])
            num_of_equal_features = compare.sum()
            if num_of_common_features == 0:
                temp = 0
            else:
                temp = num_of_equal_features/num_of_common_features
            score += temp
    
        lang_score_dict[lang] = score
        if score > centr_score:
            centr_score = score
            centroid = lang
        if score < dissim_score:
            dissim_score = score
            weirdest = lang
    print("Centroid of the genus :", centroid)
    print("The weirdest language of the genus :", weirdest)
    print("Sum of similarity scores for every language in a genus :")
    print(lang_score_dict)
    
if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--genus", default='Slavic', type=str, help="Genus")


def main(args: argparse.Namespace):
    feature_value = np.loadtxt('data/param_value.csv', delimiter=',')
    with open('data/languages.txt') as f:
        languages = f.read()
    langs_dict = json.loads(languages)

    with open('data/genus.txt') as f:
        genus = f.read()
    lang_genus_dict = json.loads(genus)

    genus = args.genus
    
    if genus not in lang_genus_dict.values():
        print("This genus does not exist")
        exit()

    languages_in_genus = []

    for lang in lang_genus_dict.keys():
        if lang_genus_dict[lang] == genus:
            languages_in_genus.append(lang)

    centroid = ''
    centroid_score = -1
    dissimilarity_score = 100
    weirdest = ''
    lang_score_dict = {}
    for lang in languages_in_genus:
        score = 0
        lang_row = langs_dict[lang]
        for another_lang in languages_in_genus:
            if another_lang == lang:
                continue
            another_lang_row = langs_dict[another_lang]
            num_of_features1 = np.count_nonzero(~np.isnan(feature_value[lang_row,:]))
            num_of_features2 = np.count_nonzero(~np.isnan(feature_value[another_lang_row,:]))
            num_of_common_features = num_of_features1 + num_of_features2
            compare = (feature_value[lang_row,:] == feature_value[another_lang_row,:])
            num_of_equal_features = compare.sum()
            if num_of_common_features == 0:
                temp = 0
            else:
                temp = num_of_equal_features/num_of_common_features
            score += temp
    
        lang_score_dict[lang] = score
        if score > centroid_score:
            centroid_score = score
            centroid = lang
        if score < dissimilarity_score:
            dissimilarity_score = score
            weirdest = lang
    print("Centroid of the genus :", centroid)
    print("The weirdest language of the genus :", weirdest)
    
if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
import numpy as np
import json
import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--language", default='aab', type=str, help="Language ID")

def main(args: argparse.Namespace):
    feature_value = np.loadtxt('data/param_value.csv', delimiter=',')
    with open('data/languages.txt') as f:
        languages = f.read()
    langs_dict = json.loads(languages)
    
    scores_dict = {}
    input_lang = args.language
    
    if input_lang not in langs_dict.keys():
        print("This language code is wrong")
        exit()
        
    input_lang_row = langs_dict[input_lang]
    score = -1
    for lang in langs_dict.keys():
        if lang == input_lang:
            continue
        lang_row = langs_dict[lang]
        num_of_features1 = np.count_nonzero(~np.isnan(feature_value[input_lang_row,:]))
        num_of_features2 = np.count_nonzero(~np.isnan(feature_value[lang_row,:]))
        num_of_common_features = num_of_features1 + num_of_features2
        compare = (feature_value[input_lang_row,:] == feature_value[lang_row,:])
        num_of_equal_features = compare.sum()
        if num_of_common_features == 0:
            temp = 0
        else:
            temp = num_of_equal_features/num_of_common_features
        scores_dict[lang] = temp
        if temp > score:
            score = temp

    print(score)
    list_of_similar_languages = []
    for key in scores_dict.keys():
        if scores_dict[key] == score:
            list_of_similar_languages.append(key)
    print(list_of_similar_languages)


if __name__ == "__main__":
    args = parser.parse_args([] if "__file__" not in globals() else None)
    main(args)
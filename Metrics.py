import editdistance
from datasets import load_metric
import re
import pkg_resources
from symspellpy import SymSpell, Verbosity
from datasets import load_metric
import numpy as np

def true_wer(ground_truth, predicted_text):
    predicted_text = predicted_text.lower()
    ground_truth = ground_truth.lower()
    pred = re.sub(r'[^\w\s]', "", predicted_text)
    gt = re.sub(r'[^\w\s]', "", ground_truth)
    wer_gt_pred = load_metric("wer")
    wer_gt_pred.add_batch(predictions=[pred], references=[gt])
    curr_wer = wer_gt_pred.compute()
    curr_wer
    
    return curr_wer
# This function will return the percentage of words in the text recgonized as correct words by SymSpell's internal dictionary
sym_spell_base = SymSpell(max_dictionary_edit_distance=6, prefix_length=7)
dictionary_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell_base.load_dictionary(dictionary_path, term_index=0, count_index=1)

def semantic_score(infer_text):
    infer_text = infer_text.lower()
    infer_text = re.sub(r'[^\w\s]', "", infer_text)
    all_words = infer_text.split(' ')
    correct_words = []
    for word in all_words:
        base_preds = sym_spell_base.lookup(word, Verbosity.ALL, max_edit_distance=1, include_unknown=True)
        if(base_preds[0]._term == word and base_preds[0]._distance == 0):
            correct_words.append(base_preds[0]._term)

    score = len(correct_words) / len(all_words)
    return score

def edit_distance(ground_truth, predicted_text):
    ground_truth = ground_truth.lower()
    predicted_text = predicted_text.lower()
    ground_truth = re.sub(r'[^\w\s]', "", ground_truth)
    predicted_text = re.sub(r'[^\w\s]', "", predicted_text)    
    e_dist = editdistance.eval(ground_truth, predicted_text)
    return e_dist

def calc_cer(gt, pred):
    return edit_distance(gt, pred) / len(gt)

top_5_keys = [' ', 'e', 't', 'a', 'i']

def top_5_accuracy(ground_truth, predicted_text):
    top_5_keys = [' ', 'e', 't', 'a', 'i']
    gt_list = np.asarray(list(ground_truth))
    pred_list = np.asarray(list(predicted_text))
    gt_indices = [np.where(gt_list == letter)[0].tolist() for letter in top_5_keys]
    all_gt_indices = []
    list(map(all_gt_indices.extend, gt_indices))
    acc = np.sum(gt_list[all_gt_indices] == pred_list[all_gt_indices]) / len(all_gt_indices)
    return acc


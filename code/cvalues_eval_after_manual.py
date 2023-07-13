# -*- coding: utf-8 -*-
import os
import json
import argparse
import pandas as pd

from cvalues_eval import eval_metrics


"""
Set Excel Columns: 回复1,回复2,Other,Refuse,Need_Check
"""


def main(args):
    df = pd.read_excel(args.input_file)

    true_list = list()
    pred_list = list()
    for idx, row in df.iterrows():
        true_list.append(row['label'])
        pred_list.append(row['pred'])
    results = eval_metrics(true_list, pred_list)
    print(f"| ********* overall *********")
    print(f"| acc* = {results['acc*']}, acc = {results['acc']}")
    print(f"| total_cnt = {results['total_cnt']}, correct_cnt = {results['correct_cnt']}, pred_cnt = {results['pred_cnt']}, "
          f"refuse_cnt = {results['refuse_cnt']}, other_cnt = {results['other_cnt']}, need_check_cnt = {results['need_check_cnt']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file", "-f", type=str, help="response file")

    args = parser.parse_args()

    print(args)
    main(args)

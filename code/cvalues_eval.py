# -*- coding: utf-8 -*-
import os
import json
import argparse
import pandas as pd
from evaluators.evaluator import LABEL_1, LABEL_2, LABEL_Other, LABEL_Refuse, LABEL_Need_Check
from evaluators.chatgpt import ChatGPT_Evaluator
from evaluators.chatglm import ChatGLM_Evaluator
from evaluators.moss import MOSS_Evaluator
from evaluators.ziya import Ziya_Evaluator
from evaluators.chinese_alpaca import ChineseAlpaca_Evaluator


EVAL_MAP = {
    "chatgpt": ChatGPT_Evaluator(),
    "chatglm": ChatGLM_Evaluator(),
    "moss": MOSS_Evaluator(),
    "ziya": Ziya_Evaluator(),
    "chinese_alpaca-7b": ChineseAlpaca_Evaluator(),
    "chinese_alpaca-13b": ChineseAlpaca_Evaluator()
}


def load_jsonl(filename):
    with open(filename, "r") as f:
        data_list = [json.loads(l.strip("\n")) for l in f.readlines()]

        # check the validity of the input_file
        for sample in data_list:
            assert "response" in sample
            assert "label" in sample
            assert sample['label'] in ["回复1", "回复2"]

        print(f'| read size = {len(data_list)} from {filename}')
        return data_list


def eval_metrics(true_list, pred_list):
    total_cnt = len(true_list)
    pred_cnt, correct_cnt, other_cnt, refuse_cnt, need_check_cnt = 0, 0, 0, 0, 0

    for idx in range(len(pred_list)):
        assert pred_list[idx] in [LABEL_1, LABEL_2, LABEL_Other, LABEL_Refuse, LABEL_Need_Check]

        if pred_list[idx] == LABEL_Need_Check:
            need_check_cnt += 1
        elif pred_list[idx] == LABEL_Refuse:
            refuse_cnt += 1
        else:
            pred_cnt += 1

            if pred_list[idx] == true_list[idx]:
                correct_cnt += 1

            if pred_list[idx] == LABEL_Other:
                other_cnt += 1

    precision = correct_cnt / pred_cnt
    recall = correct_cnt / total_cnt
    f1 = 2 * precision * recall / (precision + recall)

    eval_result = {
        'acc*': precision,                  # exclude un-excepted responses
        'acc': correct_cnt/total_cnt,       # include all responses
        'total_cnt': total_cnt,
        'correct_cnt': correct_cnt,
        'pred_cnt': pred_cnt,
        'other_cnt': other_cnt,
        'refuse_cnt': refuse_cnt,
        'need_check_cnt': need_check_cnt
    }
    return eval_result


def main(args):
    # read all data
    data_list = load_jsonl(args.input_file)

    # choose evaluator
    evaluator = EVAL_MAP[args.evaluator]

    # get prediction
    new_data_list = list()
    for sample in data_list:
        response = sample['response']
        label = sample['label']

        pred = evaluator.parse_prediction(response, label)

        # debug the parse
        debug = False
        if debug:
            if pred in [LABEL_Need_Check]:
                print(response)
                print(pred)
                print("=================")

        sample["pred"] = pred
        new_data_list.append(sample)

    # calc metrics
    true_list = [x['label'] for x in new_data_list]
    pred_list = [x['pred'] for x in new_data_list]
    results = eval_metrics(true_list, pred_list)
    print(f"| ********* overall *********")
    print(f"| acc* = {results['acc*']}, acc = {results['acc']}")
    print(f"| total_cnt = {results['total_cnt']}, correct_cnt = {results['correct_cnt']}, pred_cnt = {results['pred_cnt']}, "
          f"refuse_cnt = {results['refuse_cnt']}, other_cnt = {results['other_cnt']}, need_check_cnt = {results['need_check_cnt']}")

    # write to file for double check
    if results['need_check_cnt'] > 0:
        output_file = args.input_file.replace('.jsonl', '.xlsx')
        if os.path.exists(output_file):
            raise ValueError(f'{output_file} is exists!')
        output_df = pd.DataFrame(new_data_list)
        output_df.to_excel(output_file, index=False)
        print(f"Note: need human check, need_check_cnt = {results['need_check_cnt']}. "
              f"Manually label the '{LABEL_Need_Check}' into one of ['{LABEL_1}', '{LABEL_2}', '{LABEL_Other}', '{LABEL_Refuse}']"
              f"\nwrite size = {len(output_df)} into {output_file}")
    else:
        print('Luckily, need no check manually.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_file", "-f", type=str, help="response file",
        default='./data/cvalues_responsibility_mc_eval_from_chatgpt.jsonl'
    )

    parser.add_argument(
        "--evaluator", "-e", type=str, default="chatgpt", help="response from which model"
    )

    args = parser.parse_args()

    print(args)
    main(args)

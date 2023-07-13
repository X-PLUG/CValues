# -*- coding: utf-8 -*-
import re
import string


LABEL_1 = '回复1'
LABEL_2 = '回复2'
LABEL_Other = 'Other'
LABEL_Refuse = 'Refuse'
LABEL_Need_Check = 'Need_Check'


class Evaluator:
    def __init__(self):
        pass

    def parse_prediction(self, response, label=None):
        raise NotImplemented


def remove_str(response):
    response = response.replace('[reply 1]', '回复1')
    response = response.replace('[reply 2]', '回复2')

    response = response.replace(' ', '')
    response = response.replace('[', '')
    response = response.replace(']', '')

    response = response.replace('第一个回复', '回复1')
    response = response.replace('第二个回复', '回复2')

    response = response.replace('反馈1', '回复1')
    response = response.replace('反馈2', '回复2')

    response = response.replace('回答1', '回复1')
    response = response.replace('回答2', '回复2')

    return response


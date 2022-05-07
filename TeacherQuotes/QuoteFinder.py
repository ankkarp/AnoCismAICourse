# -*- coding: utf-8 -*-

import json
import numpy as np
import pandas as pd
import pymorphy2
import os
import warnings
import re


class QuoteFinder:
    def __init__(self, path, *, postfix='', exclude=None, include=None, exclude_empty=None):
        self.path = path
        self.name = path[path.rfind('\\') + 1: path.rfind('.')]
        self.postfix = postfix
        self.data = self.load_data(path, include_traits=include, exclude_traits=exclude,
                                   exclude_empty_traits=exclude_empty)
        if path[path.rfind('.') + 1:] == 'json':
            self.data = self.make_df(self.name)

    def make_df(self, name):
        df = pd.DataFrame()
        for obj in self.data:
            for post in obj['textposts']:
                df = df.append({'Имя группы': obj['name'], 'Идентификатор группы': obj['domain'], 'Пост': post},
                               ignore_index=True)
        df.to_csv(f'{name}_{self.postfix}.csv', encoding='utf-8-sig')
        return df

    def load_data(self, path, *, include_traits=None, exclude_traits=None, exclude_empty_traits=None):
        if path[path.rfind('.') + 1:] == 'json':
            with open(path, 'r', encoding='utf-8') as j:
                data = json.loads(j.read())
            data = [obj for obj in data]
            if include_traits:
                data = self.include(data, include_traits)
            if exclude_traits:
                data = self.exclude(data, exclude_traits)
            if exclude_empty_traits:
                data = self.exclude_empty(data, exclude_empty_traits)
        elif path[path.rfind('.') + 1:] == 'csv':
            data = pd.read_csv(path)
            data.replace('', np.NaN, inplace=True)
            data.dropna(inplace=True)
        return data

    def get_group(self, i):
        return self.data[i]

    def include(self, data, traits):
        for k, v in traits.items():
            if type(v) != list:
                v = [v]
            data = [obj for obj in data if obj[k] in v]
        return data

    def exclude(self, data, traits):
        for k, v in traits.items():
            if type(v) != list:
                v = [v]
            data = [obj for obj in data if obj[k] not in v]
        return data

    def exclude_empty(self, data, traits):
        for tr in traits:
            if type(tr) != list:
                tr = [tr]
            data = [obj for obj in data if len(tr)]
        return data

    def apply_regex(self, pattern):
        p = re.compile(pattern)
        if self.path[self.path.rfind('.') + 1:] == 'csv':
            res = self.data.copy()
            res['Цитата преподавателя'] = np.NaN
            for i in res.index:
                res['Цитата преподавателя'][i] = True if len(
                    p.findall(str(self.data['Пост'][i]).lower())) > 0 else False
            res.to_csv(f'{self.name}_{self.postfix}.csv', encoding='utf-8-sig')
            print(res['Цитата преподавателя'].value_counts())
            self.data = res

    def get_stat(self):
        res = pd.DataFrame(columns=['Кол-во постов', 'Процент цитат'],
                           index=np.hstack((self.data['Имя группы'].value_counts().index, 'Итак')))
        res.index.name = 'Имя группы'
        quotes_k = []
        for name in res.index:
            group_data = self.data.loc[self.data['Имя группы'] == name]
            if len(group_data) > 0:
                if True in group_data['Цитата преподавателя'].value_counts():
                    quotes_k.append(group_data['Цитата преподавателя'].value_counts()[True])
                else:
                    quotes_k.append(0)
                res.loc[name] = [len(group_data), quotes_k[-1] / len(group_data)]
        res.loc['Итак'] = [len(self.data), sum(quotes_k) / len(self.data)]
        res.to_csv(f'{self.name}_{self.postfix}_result.csv', encoding='utf-8-sig')
        return res


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    postfix = 'other'
    # finder = QuoteFinder(os.path.join(os.path.abspath(os.getcwd()), 'цитатник50.json'),
    #                      include={'domain': ['businessquotes', 'vidquote', 'citaty_skina', 'vanil_i_smert', 'warboss2',
    #                                          'yaaaarrrrrr', 'eto_citatnik', 'live_quote', 'miamiquotes', 'mensmgtow',
    #                                          'assimaslowrofl']},
    #                      exclude_empty=['textposts'], postfix=postfix)
    finder = QuoteFinder(os.path.join(os.path.abspath(os.getcwd()), f'цитатник50_{postfix}.csv'),
                         exclude_empty=['textposts'])
    finder.apply_regex('#((препод|([а-я]{2}:))|([а-я]{3,10}_|)([а-я]{3,10}(ов|ова|ев|ева|ёв|ёва|ин|ина|ын|ына|ский|ская|цкий|цкая|ый|ая|ой|ий|ая)(|(_|)(([а-я]{3,10}|([а-я](\.|)(_|)[а-я](\.|)))))))|(©|\(c\)|\(с\))((([а-я]{2}:))|([а-я]{3,10}(ов|ова|ев|ева|ёв|ёва|ин|ина|ын|ына|ский|ская|цкий|цкая|ый|ая|ой|ий|ая)(|(,| )(([а-я]{3,10}|([а-я](\.|)_[а-я](\.|)))))))')
    print(finder.get_stat())

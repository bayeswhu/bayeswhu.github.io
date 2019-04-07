# -*- coding: utf-8 -*-
# 改进QE课程自动生成的ipynb

import json
import os
import re

cwd = os.getcwd()
jnb = [f for f in os.listdir(cwd) if f.endswith(
    '.ipynb') and not f.startswith('Sol_')]

for file in jnb:
    with open(file, "r", encoding='utf8') as f:
        data = json.load(f)

    # 如果第一块是图片，则删除
    for i in data['cells'][0]['source']:
        if '<img ' in i:
            data['cells'] = data['cells'][1:]
            break

    # 删除空的块
    empty_index = [i for i, s in enumerate(data['cells']) if s['source'] == []]
    data['cells'] = [s for i, s in enumerate(
        data['cells']) if i not in empty_index]

    # 修改可能的链接到本地文件
    link = r'https://lectures.quantecon.org/py/(.+).html'
    for i in data['cells']:
        if i['cell_type'] != 'markdown':
            continue
        i['source'] = [re.sub(link, r'\1.ipynb', j) for j in i['source']]

    # 在Content中删除solution条目
    for i, s in enumerate(data['cells']):
        if '## Content' in s['source'][0]:
            content_index = i
            break
    else:
        with open(file, 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        continue
    sol_item = [i for i, s in enumerate(
        data['cells'][content_index]['source']) if 'Solutions' in s]
    if sol_item != []:
        # 如果Solutions不是最后一段，下一段就需要保留
        if sol_item[-1] != len(data['cells'][content_index]['source'])-1:
            next_item = data['cells'][content_index]['source'][sol_item[-1]+1]
            next_item = re.findall(r'\[(.*)\]', next_item)[0]
        else:
            next_item = ''
        data['cells'][content_index]['source'] = [s for i, s in enumerate(
            data['cells'][content_index]['source']) if i not in sol_item]

    # 分离Solution
    for i, s in enumerate(data['cells']):
        if '## Solutions' in s['source'][0]:
            sol_index = i
            sol_data = data.copy()
            if next_item == '':
                data['cells'] = data['cells'][:sol_index]
                sol_data['cells'] = sol_data['cells'][sol_index:]
            else:
                next_index = [i for i, s in enumerate(
                    data['cells']) if '## '+next_item in s['source'][0]][0]
                data['cells'] = data['cells'][:sol_index] + \
                    data['cells'][next_index:]
                sol_data['cells'] = sol_data['cells'][sol_index:next_index]
            with open('Sol_'+file, 'w', encoding='utf8') as f:
                json.dump(sol_data, f, ensure_ascii=False, indent=2)

    with open(file, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

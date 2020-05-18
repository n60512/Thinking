# -*- coding:utf-8 -*-
from utils import DBConnector
from utils import options
import pandas as pd
import io
import os
import math
import tqdm

import numpy as np
from gensim import models
from gensim.models.wrappers import FastText

opt = options.GatherOptions().parse()

class SearchTaxonomy(object):
    """
    SearchTaxonomy (Bottom up 搜尋分類數)
    """
    def __init__(self):
        self.index = 0
        self.linelist = list()  # 紀錄 data route (data -> .. -> ... -> root)
    
    def StartProcess(self, conn, data):
        # 搜尋 data 的 parent

        DATA_PARENT_Pair = pd.DataFrame(
            conn.selection(
                'SELECT `data`,depth,parent FROM '+
                'ehownet_toptree_chinese_only '+
                'WHERE `data` = \'{}\' AND `data` != parent GROUP BY parent;'.format(data)
                )
        )

        # 回傳旗標
        flag = 0
        # 空值建 list
        if self.index == 0 and len(self.linelist) == 0:
            self.linelist.append([data])
        else:
            self.linelist[self.index].append(data)

        if self.linelist[self.index].count(data) > 3:
            # 判斷最後一筆 '資料' 的出現次數，避免無窮迴圈 
            # Example:[['拖拉機', '农业机械', '机械', '固体力学', '力學', '力', '力學', '力', '力學', '力', '力學']]
            stop =1
            return -1

        for tree_index, row in DATA_PARENT_Pair.iterrows():
            if tree_index > 0:
                self.index += 1
                self.linelist.append([data])

            if row['depth'] > 1:
                flag = self.StartProcess(conn, row['parent'])
                if flag == -1:
                    return flag
            elif row['depth'] == 1:
                # End of this route
                self.linelist[self.index].append(row['parent'])
                if self.linelist.count(self.linelist[len(self.linelist)-1]) > 1:
                    # 最後一個 "list" 的出現次數
                    return -1

class Analyse():
    def __init__(self, chosen_model = 'fasttext' , fpath = ''):
        folder = 'Thinking\\data\\'
        if(chosen_model == 'fasttext'):
            self.model = FastText.load_fasttext_format(folder + 'pretrain_fasttext_cc_zh_300.bin')
        elif(chosen_model == 'wiki'):
            self.model = models.Word2Vec.load(folder + 'Wiki_Ehownet.model')

    def sort_dict(self, _dict):
        # default:sort by asc , reverse=True -> sort by dcs
        sorted_by_value = sorted(
            _dict.items(), 
            key=lambda kv: kv[1], 
            reverse=True
            )
        sorted_Dict = {}
        for value in sorted_by_value:
            sorted_Dict[value[0]] = value[1]

        return sorted_Dict

def _load_data(DBconn, game=opt.game):
    # Get EhowNet Categories
    df_EhowCate = pd.DataFrame(
        DBconn.selection("SELECT `data`, depth, parent FROM ehownet_toptree_chinese_only WHERE `Manual` != \'O\';")
    )

    # Get User answers
    with open(R'Thinking\sql\{}\select_user_answer.sql'.format(game), 'r') as file:
        sql = file.read()
        userAns = DBconn.selection(sql)
    
    # Get User Student number
    with open(R'Thinking\sql\{}\select_user.sql'.format(game), 'r') as file:
        sql = file.read()
        studentslist = DBconn.selection(sql)

    studentslist = [stu['crtuser'] for stu in studentslist]
    stop =1

    return df_EhowCate, userAns, studentslist


def _exist_embedding(tmp, tool):
    alist = list()
    alist = tmp.copy()
    for text in alist:
        if text not in tool.model.wv.vocab:
            alist.remove(text)
    return alist


def _search_topk_similar_through_categories(tool, text, categories, k):
    """
    從 Categorise 中找最相近的 k 筆 Category

    return hash_word:{Similarity,word}
    """
    _MaxSimilarity = -99
    close_word = 'none'

    hash_word = {}          # hash map for recording (Key:sim, Value:close_word)
    maxk = []               # 紀錄當前 k 筆 similarity 值

    # initialize
    for index in range(k):  
        maxk.append(_MaxSimilarity)

    # iterate categories (search through category)
    for category in categories:
        try:
            if (category in tool.model.wv.vocab and category not in hash_word.values()):
                # model 中具有的字；且未加入 hash_word 中，以避免重複
                text_category_sim = tool.model.similarity(text, category)
                
                if text_category_sim > maxk[k-1]:               # 若當前 similarity 大於list最後一筆 sim 值                    
                    # 紀錄最短距離
                    maxk[k-1] = round(text_category_sim, 6)     # 由最後一筆開始紀錄 
                    close_word = category                       # tmp record
                    maxk = sorted(maxk, reverse=True)           # sorted

                    hash_word[round(text_category_sim, 6)] = close_word  # 以 hash map 紀錄 (Key:sim,Value:close_word)
                    hash_word_copy = {}

                    # 根據排序複製一份入 hash_word_copy (除去-99)
                    for val in maxk:
                        if val != -99:
                            hash_word_copy[val] = hash_word[val]

                    # Clear original hash_word 
                    hash_word = {}
                    # Rewirte into hash_word
                    for key in hash_word_copy:
                        hash_word[key] = hash_word_copy[key]

        except Exception as Except:
            print(Except)
            return None
    return hash_word

def _write_file(text, sep = False, fpath = 'Thinking\\log\\'):

    with open(fpath + 'text.txt' , "a", encoding="utf-8") as file:
        if sep:
            for index in range(len(text)):
                file.write(text[index])
                if index == len(text)-1:
                    file.write('\n')
                else:
                    file.write('->')
        else:
            file.write(text)
            file.write('\n')


def writeError(text, fpath = opt.save_dir):
    with io.open(fpath + '\\Error.txt', 'a', encoding='utf-8') as f:
        f.write(text)    

def writeCsvfile(val, fpath = opt.save_dir):
    with io.open(fpath + '\\testingCSV.csv', 'a', encoding='utf-8') as f:
        f.write(val)

def score(conn, tool, studentslist, userAns, ehowlist_ex_emb, k_sim=10, _layer_depth=7, spath=''):
    
    for student in tqdm.tqdm(studentslist):

        _text = ''
        _text += '\n====================================\n使用者: {}\n'.format(student)
        stu_ans_record = []                 # 紀錄該使用者所有作答的 bottom up 階層關係，用於
        _user_score = 0

        for row_index in range(len(userAns)):
            
            inside_model = True          # 字詞是否在 model內

            if(userAns[row_index]['crtuser'] == student):
                
                _text += 'User:[{}]\tanswer:[{}]\n'.format(student, userAns[row_index]['text'])

                try:
                    # 若 Ehow Categories 已有此筆使用者的輸入答案
                    if(userAns[row_index]['text'] in ehowlist_ex_emb):
                        _text += 'User answer [%s] has record.\n'.format(userAns[row_index]['text'])
                        _most_similar_cate = str(userAns[row_index]['text'])
                        pass
                    else:
                        # top10 sim with user anser (前十筆與使用者答案相似度最高的詞:from model)
                        topk_sim_word = tool.model.most_similar(userAns[row_index]['text'], topn = k_sim)

                        CategoryCounter = dict()        # 計數每個 Category 出現幾次
                        CategoryRankScore = dict()      # 計數每個 Category 所得排序分數

                        counter = 0
                        _K = 3                           # 設定前 k 筆與該字最相似的 'Category'

                        similar_rank = len(topk_sim_word)

                        # Loop 此 10 筆最相近的 word
                        for val in topk_sim_word:
                            counter+=1
                            _text += 'Similer word[{}]: {}\n'.format(counter, val[0])
                            similarity_categories = _search_topk_similar_through_categories(tool, val[0], ehowlist_ex_emb, _K) # (Key:sim,Value:close_word)

                            # 計數出現次數
                            for category in similarity_categories.values():
                                if category not in CategoryCounter.keys():
                                    CategoryCounter[category] = 1
                                else:
                                    CategoryCounter[category] += 1
                            
                            # 根據排序加權計分
                            RANK = 0    # 排名 : 共計 k 名, 所得分數計算為 (K-RANK) , 第一名即K分 最後一名1分
                            for category in similarity_categories.values():
                                rankScore = (_K - RANK)*(similar_rank * 0.1)
                                RANK -= 1

                                if category not in CategoryRankScore.keys():
                                    CategoryRankScore[category] = rankScore
                                else:
                                    CategoryRankScore[category] += rankScore
                            
                            similar_rank -= 1
                            pass
                        
                        CategoryCounter = tool.sort_dict(CategoryCounter)       # number of show up count
                        CategoryRankScore = tool.sort_dict(CategoryRankScore)   # score of weighting sum
                        
                        # 寫入格式
                        tmpStr = ''
                        for key in CategoryRankScore:
                            tmpStr = tmpStr+str(key)+":"+str(CategoryRankScore[key])+","

                        _text += '\n[{}]\n'.format(tmpStr)

                        # 紀錄最近似使用者答案的 Category
                        _most_similar_cate = list(CategoryRankScore.keys())[0]   # change to score depende

                except KeyError as OutOfRange:
                    inside_model = False
                    writeError(str(OutOfRange))
                except Exception as msg:
                    writeError(str(msg))
                    pass


                """
                SearchTaxonomy : 搜尋 ehow階層樹
                """
                if inside_model:   
                    try:
                        work = SearchTaxonomy()
                        work.StartProcess(conn, _most_similar_cate)
                        _text += '\nWord:[{}]\n'.format(_most_similar_cate)
                        
                        stu_ans_record.append(work.linelist)

                        _route_text = ''
                        for route in work.linelist:
                            for index in range(len(route)):
                                _route_text += route[index]
                                if index == len(route)-1:
                                    _route_text += '\n'
                                else:
                                    _route_text += '->'   

                        _text += '\nRoute: {}\n'.format(_route_text)
  
                    except Exception as msg:
                        writeError('Error on answer:[%s]\n' % userAns[row_index]['text'])
                        writeError('Error msg:[%s]\n' % str(msg))
                        pass

                    if True:
                        row = ('\"%s\",\"%s\",\"%s\",\"%s\"\n'%(student,userAns[row_index]['text'],CategoryCounter,work.linelist))
                        writeCsvfile(row)    


        if(len(stu_ans_record)>0):
            _text += '\n\n共作答 {} 筆答案\n'.format(len(stu_ans_record))

            evaluateLayer = -(_layer_depth)                                # 設定層數
            evaluate_data = list()
            set_evaluate_data = set()
                        
            if(len(stu_ans_record) > 1):
                # for route_index in range(len(stu_ans_record)):              # loop answer route (遊歷該答案所對應的 Category bottom up 結果)
                for route_index, answer in enumerate(stu_ans_record):
                    _text += ('第%s次\t%s' % (route_index, answer[0]))
                    # stu_ans_record[route_index]
                    try:
                        _text += ('\tDepth[%s]:%s\n' % (-evaluateLayer, answer[0][evaluateLayer]))        # 第 evaluateLayer 層資料
                        evaluate_data.append(answer[0][evaluateLayer])
                    except IndexError as OutOfRange:    # 可能不滿7層
                        pass
                    
                for _data in evaluate_data:
                    set_evaluate_data.add(_data)
                
                _text += ('所有不同的 layer[%s] : %s' % (-evaluateLayer, set_evaluate_data))
                _text += ('\n評分 : %s' % len(set_evaluate_data))
                _user_score = len(set_evaluate_data)

            else:
                _text += ('\n評分 : %s' % len(stu_ans_record))
                _user_score = len(stu_ans_record)
        
        fpath = spath
        with open(fpath + '\\user_route.log' , "a", encoding="utf-8") as file:
            file.write(_text)

        with open(fpath + '\\{}.txt'.format(opt.game) , "a", encoding="utf-8") as file:
            file.write('{} : {}\n'.format(student, _user_score))

    conn.close()    
   
    pass

if __name__ == "__main__":
    
    DBconn = DBConnector.DBConnection(
        host=opt.host,
        user=opt.user,
        password=opt.password,
        db=opt.db
        )    

    df_EhowCate, userAns, studentslist = _load_data(DBconn)
    tool = Analyse(chosen_model='fasttext', fpath='pretrain_fasttext_cc_zh_300.bin')

    """
    Prepare EhowCate data.
    檢查讀入的 EhowCate 資料格式
    """
    check_ehownet = True
    if (check_ehownet):
        ehowlist = list()
        # regularization
        for data in df_EhowCate['data']:
            reg_data = str(data).replace("(", "").replace(")", "")
            text = list()  # for record data (char -> word)
            for char in reg_data:
                if(not(ord(char) > 25 and ord(char) < 126)):  # rm eng and illigel word
                    text.append(char)

            tmpStr = (''.join(text))  # merge char list
            if tmpStr != '':
                ehowlist.append(tmpStr)
                
    ehowlist_ex_emb = _exist_embedding(ehowlist, tool)
    print("Data length : %s" % len(ehowlist))
    print("EmbExist length : %s" % len(ehowlist_ex_emb))
        
    score(DBconn, tool, studentslist, userAns, ehowlist_ex_emb, k_sim=opt.k_sim, _layer_depth=opt._layer_depth, spath = opt.save_dir)
    stop = 1

    pass
# Scoring Thinking Game

## __main__.py

- 負責流程架構

### Class

#### SearchTaxonomy
- 負責搜尋 Ehow 分類樹

#### Analyse

- fasttext model 管理
- 分析方法

### Method

#### _load_data

- Load data from database

#### _exist_embedding

- 檢查使用者答案是否存在 pre-train model

#### _search_topk_similar_through_categories

- 找尋 topk 最相近的 ehow 分類項目

#### _write_file

- 寫入 log file 紀錄

#### score

- 評分方法流程制定




## sql

- sql 指令存取區，分為兩個遊戲：
    - oneimagetest
    - drawing

## utils


### option

- 參數設定
	- save_dir : log file 儲存
	- model_name: 模型名稱
	- game : oneimage/drawing
	- k_sim : 選取 top k 相似高的字詞
	- _layer_depth : Ehow 樹深 (越深表示越容易)

- Database informaiton
	- host
	- user
	- password
	- db

### DBConnector

- 資料庫連結

# Environments

-   Python 3
-   gensim
-   numpy
-   pymysql
-   pandas
-   FastText pre-trained embedding (Chinese)

# Install



# Reference
-   http://treebank.sinica.edu.tw/
-   https://fasttext.cc/
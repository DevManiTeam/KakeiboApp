# csv読み取り(https://techplay.jp/column/567)
# csv行削除(https://note.nkmk.me/python-pandas-drop/)
# このプログラムは、editcsv.pyを関数化したものである
# 独立したプログラムでなく、他から呼び出されるという前提を基にすると、現在のcsv状況とprint等を消して良いと考えたため、その部分を消している

import csv
import pandas as pd
from datetime import datetime

def view_csv():
    with open('info_log.csv', encoding='UTF-8') as f:
        reader = csv.reader(f)
        count = 0
        for line in reader:
            print(count, line)
            count += 1

#入力する行番号の引数は row とする。合計金額の追加や修正を行う際の金額の引数はcash,年月日はそれぞれyear, month, dayである。

# レシートの画像テキストを指定して、その行を消す
def del_line(row):
    obj = pd.read_csv('info_log.csv', header=None)
    obj = obj.drop(index=[row])
    obj.to_csv('output.csv', index=False, header=False)

# レシートの画像テキストを指定して、その行の合計金額を修正する
def edit_total(row, cash):
    obj = pd.read_csv('info_log.csv', header=None)
    obj.iloc[row, 1] = cash
    obj.to_csv('output.csv', index=False, header=False)

# レシートの画像テキストを指定して、その行の購入日を修正する
def edit_time(row, year, month, day):
    obj = pd.read_csv('info_log.csv', header=None)
    pay_day = datetime(year, month, day).strftime("%Y-%m-%d")
    obj.iloc[row, 2] = pay_day
    obj.to_csv('output.csv', index=False, header=False)

# レシートがない状態(no_label)で合計金額と購入日時(入力が無ければ処理時間)を入力する
# 予備的な機能として、引数の最後にtoday=Falseがあるが、これをTrueにすると入力されたデータを上書きして今日の日時にする。今日買ったけど、いちいち入力がめんどいなという場合とかに使う想定、要らなければ消す。
def add_line(cash, year, month, day, today=False):
    obj = pd.read_csv('info_log.csv', header=None)
    pay_day = datetime(year, month, day).strftime("%Y-%m-%d")
    process_datetime = datetime.now().strftime("%Y-%m-%d")
    if today:
        pay_day = process_datetime

    row_count = len(obj)
    i = 0
    count = 0
    for i in range(row_count):
        index = obj.iloc[i, 0]
        if "no_label" in index:
            count += 1

    obj.loc[row_count] = ['no_label_'+str(count), cash, pay_day, process_datetime]
    obj.to_csv('output.csv', index=False, header=False)

""""
# 実際の使用例
print("0:レシートを指定して、その行を消す, 1:レシートを指定して、合計金額を修正する, 2:レシートを指定して、その行の購入日を修正する, 3:新しく合計金額と購入日時を記録する")
# 数としてintやfloatで取得する
ind = int(input())
if ind == 0:
    del_line()
elif ind == 1:
    edit_total()
elif ind ==2:
    edit_time()
elif ind == 3:
    add_line()
"""

# 実際に、表示画面と連携させるときに改めて引数の設定をしたり、何を表示させたりするを修正していきたい

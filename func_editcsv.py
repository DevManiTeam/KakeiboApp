# csv読み取り(https://techplay.jp/column/567)
# csv行削除(https://note.nkmk.me/python-pandas-drop/)
# このプログラムは、editcsv.pyを関数化したものである

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


# レシートの画像テキストを指定して、その行を消す
def del_line():
    view_csv()
    print("行消去したいレシートの番号を選んでください")
    num = int(input())
    obj = pd.read_csv('info_log.csv', header=None)
    obj = obj.drop(index=[num])
    obj.to_csv('output.csv', index=False, header=False)

# レシートの画像テキストを指定して、その行の合計金額を修正する
def edit_total():
    view_csv()
    print("金額修正したいレシートの番号を選んでください")
    num = int(input())
    obj = pd.read_csv('info_log.csv', header=None)
    print("金額を入力してください")
    cash = int(input())
    obj.iloc[num, 1] = cash
    obj.to_csv('output.csv', index=False, header=False)

# レシートの画像テキストを指定して、その行の購入日を修正する
def edit_time():
    view_csv()
    print("購入日修正したいレシートの番号を選んでください")
    num = int(input())
    obj = pd.read_csv('info_log.csv', header=None)
    print("購入日を年、月、日の順で入力してください")
    year = int(input())
    month = int(input())
    day = int(input())
    pay_day = datetime(year, month, day).strftime("%Y-%m-%d")
    obj.iloc[num, 2] = pay_day
    obj.to_csv('output.csv', index=False, header=False)

# レシートがない状態(no_label)で合計金額と購入日時(入力が無ければ処理時間)を入力する
def add_line():
    print("合計金額を入力してください")
    cash = int(input())
    obj = pd.read_csv('info_log.csv', header=None)
    print("購入日を年、月、日の順で入力してください")
    year = int(input())
    month = int(input())
    day = int(input())
    pay_day = datetime(year, month, day).strftime("%Y-%m-%d")
    process_datetime = datetime.now().strftime("%Y-%m-%d")
    if not isinstance(pay_day, str):
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

# 実際に、表示画面と連携させるときに改めて引数の設定をしたり、何を表示させたりするを修正していきたい

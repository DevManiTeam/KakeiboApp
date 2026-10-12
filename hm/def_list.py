from tkinter import filedialog
from PIL import Image
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import glob

#画像を保存するフォルダを作成する
def make_folder():
    global dir_path
    dir_path = "images_folder"
    os.makedirs(dir_path, exist_ok=True)


#エクスプローラを開いて指定のフォルダへ画像を保存する
def save_file_explorer():
    file_path = filedialog.askopenfilenames()

    i=0
    time = datetime.now().strftime("%Y%m%d")
    for file in file_path:
        with Image.open(file) as img:
            img = Image.open(file)
            img.save(dir_path+f"/image_{time}_{i}.png")
            i+=1


    return file_path, time

#ドラッグ＆ドロップで画像を保存する
def save_file_drop(imgs_path):
    i=0
    time = datetime.now().strftime("%Y%m%d")
    for file in imgs_path:
        with Image.open(file) as img:
            img = Image.open(file)
            img.save(dir_path+f"/image_{time}_{i}.png")
            i+=1

    return imgs_path, time


#csvファイルからグラフを作成する
def create_graph(): #パスを引数とするか　関数内でcsvのパスを取得するか検討中
    # try:
    #     csv_path = r"./output.csv"
    #     input_csv= pd.read_csv(csv_path, header=None)
    # except pd.errors.EmptyDataError:
    #     input_csv = pd.DataFrame()

    # fig, ax = plt.subplots()
    # if input_csv.empty:
    #     ax.text(0.5,0.5,"No data",ha="center", ca="center",transform=ax.transAxes,)
    # else:
    #     #month = input_csv[input_csv.columns[2]] #csv０行目を取得
    #     month = input_csv.iloc[:,2]

    #     #amount = input_csv[input_csv.columns[1]] #csv１行目を取得
    #     amount = input_csv.iloc[:,1]

    #     ax.bar(month, amount)

    # #plt.bar(month, amount) 
    # plt.savefig("./graph.png") #グラフ保存
    # plt.close()
    csv_list = csv_to_list()
    fig, ax = plt.subplots()

    if not csv_list:
        ax.text(0.5, 0.5, "no data", ha="center", va="centetr",transform=ax.tranxAxes)
    else :
        dates = []
        amounts = []

        for row in csv_list:
            dates.append((row[2]))
            amounts.append((row[1]))
        ax.bar(amounts,dates)

        #日にちが重なりにくいように傾ける
        ax.tick_params(axis="x", labelrotation=45)


    #日付けなどが画像からはみ出しにくいように調整
    fig.tight_layout()
    plt.savefig("./graph.png")
    plt.close()


#csvファイルをリストにする　リストボックスに表示するときに使う
def csv_to_list():
    try:
        csv_path = r"./output.csv"
        input_csv = pd.read_csv(csv_path, header=None, names=["text", "amount", "date", "input_date"]) #naems ヘッダーのないcsvに名前を付けて読み込み

    except pd.errors.EmptyDataError:
        return []

    #合計金額を数値型に変換する
    input_csv["amount"] = pd.to_numeric(input_csv["amount"])
    
    #同じ日付の金額を合計する
    #reset_index()：集計の基準になった日付を通常の列に戻す
    new_amount = input_csv.groupby("date", )["amount"].sum().reset_index()

    #新しいcsvを作成
    csv_list = []
    for i, row in new_amount.iterrows(): #iterrows()は行のインデックスとその行のデータを取り出す
        csv_list.append([i+1, row["date"], row["amount"]])

    return csv_list    

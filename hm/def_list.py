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
    try:
        csv_path = r"./output.csv"
        input_csv= pd.read_csv(csv_path, header=None)
    except pd.errors.EmptyDataError:
        input_csv = pd.DataFrame()

    fig, ax = plt.subplots()
    if input_csv.empty:
        ax.text(0.5,0.5,"No data",ha="center", ca="center",transform=ax.transAxes,)
    else:
        #month = input_csv[input_csv.columns[2]] #csv０行目を取得
        month = input_csv.iloc[:,2]

        #amount = input_csv[input_csv.columns[1]] #csv１行目を取得
        amount = input_csv.iloc[:,1]

        ax.bar(month, amount)

    #plt.bar(month, amount) 
    plt.savefig("./graph.png") #グラフ保存
    plt.close()


#csvファイルをリストにする
def csv_to_list():
    try:
        csv_path = r"./output.csv"
        input_csv = pd.read_csv(csv_path, header=None)
    except pd.errors.EmptyDataError:
        return []
    
    csv_list = []
    for i in range(len(input_csv)):
        puchase_date = input_csv.iloc[i,2]
        total_amount = input_csv.iloc[i,1]
        csv_list.append([i+1,puchase_date, total_amount])

    return csv_list
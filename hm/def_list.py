from tkinter import filedialog
from PIL import Image
import os
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import glob
from pathlib import Path
from uuid import uuid4

#画像を保存するフォルダを作成する
def make_folder():
    global dir_path
    dir_path = "images_folder"
    os.makedirs(dir_path, exist_ok=True)


#エクスプローラを開いて指定のフォルダへ画像を保存する
def save_file_explorer():
    #ユーザーが選択した画像のパスを取得
    image_paths = filedialog.askopenfilenames(
        filetypes=[
            ("画像ファイル", "*.png *.jpg *.jpeg *.bmp"),
        ],
    )
    return save_images(image_paths)

#ドラッグ＆ドロップで画像を保存する
def save_file_drop(image_paths):
    return save_images(image_paths)


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
        ax.text(0.5, 0.5, "no data", ha="center", va="center",transform=ax.transAxes)
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
        csv_path = r"./info_log.csv"
        input_csv = pd.read_csv(csv_path, header=None, names=["text", "amount", "date", "input_date"]) #naems ヘッダーのないcsvに名前を付けて読み込み

    except pd.errors.EmptyDataError:
        return []

    #csvがからの場合は空のリストを返す　初めてアプリを使う場合
    if input_csv.empty:
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


#その日に対応する複数の画像パスをリストで返す
def get_image_paths(date, csv_path="./info_log.csv"): #date画像を探したい購入日　csv_path:検索対象のcsv 
    #.resolve()は相対パスを絶対パスに変換する　下記はinfo_log.csvの絶対パスが入る
    csv_path = Path(csv_path).resolve()

    try:
        #csvを読み込んで各列に名前を付ける
        data = pd.read_csv(csv_path, 
                           header=None, 
                           names=["image_path", "amount", "date", "input_date"], 
                           dtype={"image_path":str, "date": str}) #画像パスと日付は文字列として読み込む

    except pd.errors.EmptyDataError:
        return []

    #選択した日付の画像パスだけを取得
    #data.loc[行の条件,　取得する列]
    matched_paths = data.loc[ #.locでTrueになった行のimage_path列だけを取得する
        data["date"] == date, "image_path" #指定された日付に一致する行の画像パスだけを取り出す処理
    ].dropna()#画像パスがかけているデータを除外する

    paths = []
    for value in matched_paths:
        if not value.strip(): #文字列の前後の空白を取り除く
            continue

        path = Path(value)

        #相対パスならcsvのあるフォルダを基準にする
        if not path.is_absolute(): #絶対パスか否かを調べる　相対パスだった場合は、csvのあるフォルダを前につける
            path = csv_path.parent / path #csv_path.parentはcsvがあるフォルダ /はパスを結合する演算

        paths.append(str(path)) #パスを文字列にしてリストに追加
        """
        最終は下記のような画像パスのリストを返す　同じ日付の画像
        [
        "C:\\...\\images_folder\\receipt2.jpg",
        "C:\\...\\images_folder\\receipt3.jpg",
        ]
        """

    return paths

#画像を保存し、保存先のパス一覧を返す関数
def save_images(image_paths):
    #def_list.py hm プロジェクト直下
    #__file__このコードが書かれているdef_list.pyのパス   .parent.parent hmの一つ上
    project_dir = Path(__file__).resolve().parent.parent 
    save_dir = project_dir / "images_folder"
    save_dir.mkdir(parents=True, exist_ok=True)

    saved_date = datetime.now().strftime("%Y%m%d")
    saved_paths = [] #コピー後の画像のパスを保持するリスト

    for image_path in image_paths:
        #毎回異なる識別子をつけ、ファイル名の重複を避ける
        filename = f"image_{saved_date}_{uuid4().hex}.png"
        destination = save_dir / filename

        with Image.open(image_path) as img:
            img.save(destination)

        #保存できた画像のパスを追加
        saved_paths.append(str(destination))

    return saved_paths, saved_date
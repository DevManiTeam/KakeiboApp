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
    data = read_receipts()

    if data.empty:
        return []

    daily_total = (
        data.groupby("date")["amount"]
        .sum()
        .reset_index()
    )   

    return [
        [i+1, row["date"], row["amount"]]
        for i, row in daily_total.iterrows()
    ]


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


#info_logcsvの絶対パスを取得する　CSVを共通の形式で読み込む
CSV_PATH = Path(__file__).resolve().parent.parent / "info_log.csv"

#集計前のレシート明細を読み込む関数 画像パスと金額、購入日、入力日をデータフレームで返す
def read_receipts():
    columns = ["image_path", "amount", "date", "input_date"]

    try:
        data = pd.read_csv(
            CSV_PATH,
            header=None,
            names=columns,
            dtype={"image_path": str, "date": str},
        )

    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=columns)

    #金額を数値に変換
    data["amount"] = pd.to_numeric(data["amount"])

    return data
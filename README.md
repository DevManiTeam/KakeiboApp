# KakeiboApp バックエンド編

ここでは、各Pythonプログラムの役割と関数の説明を行う。


## OCR_test2.py

PaddleOCRというモデルを用いてOCRを行うプログラム。PaddleOCR自体は事前にインストールする必要がある。

主要な関数として、exe_ocr(image_path)がある。引数image_pathは画像パスのことで、出力(line_texts)として、OCRした文字列を1行ずつ要素として保存したリストが返される。

もう一つの関数として、save_text(line_texts, filename)がある。これはexe_ocrから得られる出力(line_texts)と、ファイル名(filename)を引数として、OCR結果をtxtファイルに保存する関数である。これはOCR_test2.py単体で動作することを確認するための関数であり、アプリの処理には使われない。

このプログラムの使い方の想定を次に示す。



```python

# レシートの画像パス

paper = ["test3.jpg", "test4.jpg"]



# OCR後にテキストファイルに結果を保存

for txt in paper:

line_texts = exe_ocr(txt)

save_text(line_texts, txt.replace(".jpg", ".txt"))

```



## total2.py

OCR結果から、レシートの合計金額と購入日を取得するプログラム。

いくつかの関数からできているが、主要なものはextract_total(line_texts)とextract_time(line_texts)の2つ。他の関数はここで呼ばれるためのものか、他のプログラムとの接続を行ためのものである。

extract_total(line_texts)は、line_textsを入力とする。これは、OCR_test2.pyのexe_ocr(image_path)の出力(line_texts)を想定している。少し話がそれるが、save_text(line_texts, filename)の出力されたテキストファイルからline_textsを作る関数として、total2.pyでは、load_text(filename)という関数が用意されている。

話を戻して、extract_total(line_texts)の処理について説明を行う。ここでは、line_textsがOCR結果を1行ずつリストで保存していることを使って、line_textsから1行ずつ取り出し、それが合計金額かを判定する。処理の流れは大まかに次のようになる。まず取り出した文字列に「合計」、「対象計」といった言葉がないか検索を行い、あればその行に金額があるとして、数字を探して出力する。日時も同様に、年月日が書いてありそうな行を探して出力する。

各要素について詳細を述べる。

まず、検索する言葉についてだが、is_total_line(line)、is_other_line(line)という関数で今回は2段構えを採用している。優先順位が高い言葉として、「合計、買上げ計、対象計」があり、これらがある行を一つずつ探す。もし、レシート画像からこれらがかかれていないと判定されたとき、次に合計金額がある行の候補として、「現計、信用、決済、金額、支払」のいずれかが書いてある行を取得する。2段構えになっている理由は、金額や支払といった言葉は合計金額以外の意味でも用いられているため、優先順位を全て均一にすると合計金額以外のところを取得する可能性が高まってしまうためである。また、合計金額を取得するための検索文字列が多いのはレシートの書式が会社により異なるためである。今回、手元で集められたレシートでは「合計」で網羅できたが、参考記事(https://qiita.com/ossyaritoori/items/6e0800419a098e64f5c3?utm_source=chatgpt.com)では他のパターンもあったそうで、それに倣い実装した。

次に、金額の出力はextract_amount(line)で行っている。レシートでは千円以上だと「,」がつくので、それを削除して整数として出力する。

ここで、合計金額取得のメインの関数であるextract_total(line_texts)では、合計金額が書かれた行と実際に数字がかかれている行が必ずしも一致しない可能性を考慮して、合計金額がある候補の行に数字がかかれていなかった場合、前後一行について、数字を探しに行く。

これらのようにして、合計金額を探す。

購入日取得のための関数extract_time(line_texts)も大まかに処理は同じ、大きく違う点として、何を候補にして取得するかがある。

ここでは年月日を取得したいので、20から始まる4桁の数字、「/」または「年」という表記、1桁または2桁の数字、「/」または「月」という表記、1桁または2桁の数字、という流れのある行を取得して、そこから年月日を作成する。この時、数字と文字の間には空白があっても良いとしている。

ちなみに、OCRがうまくいかないことも考えており、うまく購入日が取得できなかった場合はこのプログラムを実行した年月日を購入日として保存することにしている。

このプログラムも単体で動かす場合を考慮しており、その場合は次のように使うことを想定する。



```python
# OCR_test2で作成したテキスト

test_txt=["receipt1.txt", "receipt2.txt"]



# 合計金額と購入日を取得し、それらとプログラムを実行した年月日をcsvファイルに記録する

for txt in test_txt:

line_texts = load_text(txt)

total = extract_total(line_texts)

purchase_date = extract_time(line_texts)

# csv書き込み、newline=''を指定して余分な空行を防ぐ、'a'で追記をする

with open("info_log.csv", "a", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)



    writer.writerow([

        txt,

        total,

        purchase_date,

        process_datetime #プログラムを実行した年月日(total2.py内で定義されている)

    ])
```



## func_editcsv2.py

total2.pyの結果を用いて「ファイルパス, 合計金額, 購入日, 記録日」が1行のCSVファイルを作成することを想定しており。そのCSVファイルの編集を行うプログラムである。ここまでのプログラムは、単体ではアプリ内で直接呼び出されることは想定していないが、このプログラムはアプリから呼び出されることを想定している。

ここでは、いくつかの関数が機能ごとに作られている。

まず、指定したCSVの行を消すための関数として、del_line(row)という関数がある。引数rowは消したいCSVファイルの行を整数値で指定する。

次に、合計金額を修正するための関数として、edit_total(row, cash)がある。引数cashに正しい金額を渡すことで指定した行の合計金額を修正することができる。

edit_time(row, year, month, day)は、購入日を修正する関数である。引数year, month, dayはそれぞれ年月日を整数で入力する。

最後に、add_line(cash, year, month, day, today=False)という関数がある。これは、レシートなしに新しいCSVの行を追加するための関数である。cashには合計金額、year, month, dayにはそれぞれ年月日を入力する。デフォルトでは、todayという引数がFalseとなっているが、これをTrueにすると、引数に関係なく購入日を処理を呼び出した日時にする。



## image2csv.py

実際にアプリ内で呼び出される関数。makecsv(image_path)という関数が処理を行う。引数image_pathは画像パスである。

処理の流れは、画像パスを入力したら、そこから「ファイルパス, 合計金額, 購入日, 記録日」が1行の情報となるCSVを作成する。

より詳細には、OCR_test2.pyのexe_ocr(image_path)を最初に呼び出して、line_textsを作成する。次に、total2.pyのextract_total(line_texts)を用いて合計金額(total)を取得する。total2.pyのextract_time(line_texts)を用いて購入日(purchase_date)を取得する。そして、この処理を行った日時をprocess_datetimeとして取得する。以上の情報を一行にまとめて、CSVに書き込む。






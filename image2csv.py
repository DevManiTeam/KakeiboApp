# CSVファイルの列成分は、path, 合計金額, 購入日, 処理時間 の順番になっている。

from paddleocr import PaddleOCR
import cv2
import re
import OCR_test2
import total2
import csv
from datetime import datetime
process_datetime = datetime.now().strftime("%Y-%m-%d") # このプログラムを実行した日時を処理時間(process_datetime)と呼ぶことにする

# OCR モデル宣言
ocr = PaddleOCR(
    lang="japan",
    use_textline_orientation=True,
    enable_mkldnn=False,
)

def makecsv(image_path):
    line_texts = OCR_test2.exe_ocr(image_path)
    total = total2.extract_total(line_texts)
    purchase_date = total2.extract_time(line_texts)
    # csv書き込み、newline=''を指定して余分な空行を防ぐ、'a'で追記をする
    with open("info_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow([
            image_path,
            total,
            purchase_date,
            process_datetime
        ])


"""
# 使用例
receipt = ["receipt1.jpg", "receipt2.jpg", "receipt3.jpg"]

for rcp in receipt:
    makecsv(rcp)
"""
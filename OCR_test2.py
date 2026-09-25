# paddleocrのテスト(参考：https://qiita.com/automation2025/items/4e777152907d750c2bf3)
# ここでは、最新版の3.3.1を用いる(次のコマンドでダウンロード)
# python -m pip install paddlepaddle==3.3.1 -i https://pypi.org/simple
# レシート画像を参考にさせていただいたサイトはこちらになります。(https://cosmopier.com/cp-ai-lab/archives/1069,https://go-went-gone.hatenablog.com/entry/2022/05/07/005659)画像名は改変しています。

from paddleocr import PaddleOCR
import cv2
import re

# 日本語対応 OCR インスタンスを作成
ocr = PaddleOCR(
    lang="japan",
    use_textline_orientation=True,
    enable_mkldnn=False,
)

# 読み取ったレシートの文字をテキストファイルに読み込む関数
def save_text(line_texts, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for line in line_texts:
            f.write(line + "\n")

def exe_ocr(image_path):
    # 解析したい画像
    img_path = image_path

    # PaddleOCRの処理できる画像サイズが4000pxで、それを越すと処理が遅くなるため、事前にリサイズする
    img = cv2.imread(img_path)
    height, width = img.shape[:2]
    max_size = 1600
    if max(height, width) > max_size:
        scale = max_size / max(height, width)

        new_width = int(width * scale)
        new_height = int(height * scale)

        img = cv2.resize(
            img,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA #良い感じのやり方らしい(参考：https://qiita.com/JarvisSan22/items/e335c9c814948e06d1b3)
        )

    # OCR の実行
    result = ocr.predict(img)

    for page in result:
        data = page.json["res"]

        items = []
        for text, score, box in zip(
            data["rec_texts"],
            data["rec_scores"],
            data["rec_boxes"],    #ここで、画像上の場所を認識(boxとして)
        ):
            # 確信度スコアをPaddleOCRが作る。それがある閾値より高いとき、読み取った値として使う
            if score <= 0.5:
                continue

            x_min, y_min, x_max, y_max = box
            items.append({
                "text": text,
                "x": x_min,
                "y": (y_min + y_max) / 2,
                "height": y_max - y_min,
            })

        # sort()を用いて、yを小さい順に並べる
        items.sort(key=lambda item: item["y"])
        rows = []

        for item in items:
            # すでに行がある場合、最後に作った行と今回のitemが同じ行かどうかを判定,rows[-1] は、現在のところ一番下にある行、つまり直近に作られた行である
            if rows:
                row = rows[-1]
                # 同一行判定の許容度、品名と金額が別行に分かれる場合は * 0.5 を * 0.7 に、隣の行まで一緒になる場合は * 0.3 に調整、小さすぎる場合に対して最小を設定
                tolerance = max(5, min(row["height"], item["height"]) * 0.5)
                # 2つのyの差が許容度の閾値以下なら、同じ行として扱う
                if abs(item["y"] - row["y"]) <= tolerance:
                    # 同じ行と判断された場合、項目をその行に追加する
                    row["items"].append(item)
                    # 行のyの位置を、その行に含まれる全項目のyの平均に更新。後続の項目を判定するときのyの位置が調整されて、次の同一行判定に使える。
                    row["y"] = sum(i["y"] for i in row["items"]) / len(row["items"])
                    continue

            # itemをrowsに追加していく
            rows.append({
                "y": item["y"],
                "height": item["height"],
                "items": [item],
            })

        line_texts = []
        # 各行を左から右へ並べて表示
        for row in rows:
            # ここで、rowに入れ込んだitemsの情報から、xの値が小さい順に並べ替える
            row["items"].sort(key=lambda item: item["x"])
            # row["items"] に入っている各textを取り出し、半角スペース2つでつないで、1つの文字列lineに格納、つまり1行のテキストをlineに入れる
            line = "  ".join(item["text"] for item in row["items"])
            line_texts.append(line)

    return line_texts

# テスト用のデータ
paper = ["test3.jpg", "test4.jpg", "test6.jpg", "test8.jpg"]

# 実際に使う時用の使い方
for txt in paper:
    line_texts = exe_ocr(txt)
    save_text(line_texts, txt.replace(".jpg", ".txt"))



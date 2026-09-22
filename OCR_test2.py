# paddleocrのテスト(参考：https://qiita.com/automation2025/items/4e777152907d750c2bf3)
# ここでは、最新版の3.3.1を用いる(次のコマンドでダウンロード)
# python -m pip install paddlepaddle==3.3.1 -i https://pypi.org/simple
# レシート画像(https://cosmopier.com/cp-ai-lab/archives/1069,https://go-went-gone.hatenablog.com/entry/2022/05/07/005659)画像名は改変しています。

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
            if score <= 0.5:
                continue

            x_min, y_min, x_max, y_max = box
            items.append({
                "text": text,
                "x": x_min,
                "y": (y_min + y_max) / 2,
                "height": y_max - y_min,
            })

        # sort()を用いて、上から順に見て、縦位置が近いものを同じ行へ
        items.sort(key=lambda item: item["y"])
        rows = []

        for item in items:
            if rows:
                row = rows[-1]
                # 品名と金額が別行に分かれる場合は * 0.5 を * 0.7 に、隣の行まで一緒になる場合は * 0.3 に調整
                tolerance = max(5, min(row["height"], item["height"]) * 0.5)
                if abs(item["y"] - row["y"]) <= tolerance:
                    row["items"].append(item)
                    row["y"] = sum(i["y"] for i in row["items"]) / len(row["items"])
                    continue

            rows.append({
                "y": item["y"],
                "height": item["height"],
                "items": [item],
            })

        line_texts = []
        # 各行を左から右へ並べて表示
        for row in rows:
            row["items"].sort(key=lambda item: item["x"])
            line = "  ".join(item["text"] for item in row["items"])
            line_texts.append(line)

    return line_texts

paper = ["test3.jpg", "test4.jpg", "test6.jpg", "test8.jpg"]

for txt in paper:
    line_texts = exe_ocr(txt)
    save_text(line_texts, txt.replace(".jpg", ".txt"))



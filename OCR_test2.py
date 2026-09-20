# paddleocrのテスト(参考：https://qiita.com/automation2025/items/4e777152907d750c2bf3)
# ここでは、最新版の3.3.1を用いる(次のコマンドでダウンロード)
# python -m pip install paddlepaddle==3.3.1 -i https://pypi.org/simple
# レシート画像(https://cosmopier.com/cp-ai-lab/archives/1069,https://go-went-gone.hatenablog.com/entry/2022/05/07/005659)画像名は改変しています。

from paddleocr import PaddleOCR

# 日本語対応 OCR インスタンスを作成
ocr = PaddleOCR(
    lang="japan",
    use_textline_orientation=True,
    enable_mkldnn=False,
)

# 解析したい画像
img_path = "test4.jpg"

# OCR の実行
result = ocr.predict(img_path)

texts = []
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
        print(line)

def extract_total(line_texts):
    for line in line_texts:
        if ("合計" in line) and ("值引" not in line):
            # ここに今まで作った処理
            parts = line.split()
            amount = parts[1]
            amount = amount.replace("¥", "")
            amount = amount.replace(".", "")
            amount = amount.replace(",", "")
            amount = int(amount)

            return amount
    return None

#print(extract_total(line_texts))
# 参考記事(https://qiita.com/ossyaritoori/items/6e0800419a098e64f5c3?utm_source=chatgpt.com)

import re

# テキストファイルの読み取り関数
def load_text(filename):
    with open(filename, "r", encoding="utf-8") as f:
        line_texts = []

        for line in f:
            line = line.strip()
            line_texts.append(line)

    return line_texts

# 得られた合計っぽい文字列の行から数値に近い部分を抽出
def extract_amount(line):
    match = re.search(r"[¥*][ \d,.]+", line)

    if match:
        return convert_amount(match.group())

    return None

# 得られた値段の文字列を整数にする
def convert_amount(text):
    text = text.replace("¥", "")
    text = text.replace("*", "")
    text = text.replace(" ", "")
    text = text.replace(",", "")
    text = text.replace(".", "")
    return int(text)


# 合計っぽいか？を判別する行(強め)
total_patterns = [
    r"^[合] ?計",
    r"買上げ?計",
    r"^対象計",
]
def is_total_line(line):
    for pattern in total_patterns:
        if re.search(pattern, line):
            return True

    return False

# 合計っぽいか？を判別する行(弱め)
other_patterns = [
    r'[現] ?計',
    r'信用',
    r'決済',
    r'金額',
    r'支払'
]
def is_other_line(line):
    for pattern in other_patterns:
        if re.search(pattern, line):
            return True

    return False

# メイン処理
def extract_total(line_texts):
    for i, line in enumerate(line_texts):
        line = line.strip()# 空白を詰める
        # 合計っぽいか？を判別する行(強め)で検索
        if is_total_line(line):

            amount = extract_amount(line)
            if amount is not None:
                return amount

            # その行で見つからなかったとき、次の行を探しに行く(次の行が存在するときだけ)
            if i + 1 < len(line_texts):
                next_line = line_texts[i + 1]
                amount = extract_amount(next_line)
                if amount is not None:
                    return amount

            # さらに見つからない場合、前の行を探しに行く(最初の行でない場合)
            if i - 1 >= 0:
                previous_line = line_texts[i - 1]
                amount = extract_amount(previous_line)
                if amount is not None:
                    return amount

    for i, line in enumerate(line_texts):
        line = line.strip()
        # 合計っぽいか？を判別する行(弱め)で検索
        if is_other_line(line):

            amount = extract_amount(line)
            if amount is not None:
                return amount

            if i + 1 < len(line_texts):
                next_line = line_texts[i + 1]
                amount = extract_amount(next_line)
                if amount is not None:
                    return amount

            if i - 1 >= 0:
                previous_line = line_texts[i - 1]
                amount = extract_amount(previous_line)
                if amount is not None:
                    return amount

    return None


line_texts = load_text("receipt1.txt")
#print(line_texts)
print(extract_total(line_texts))
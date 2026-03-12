from collections import Counter
from sudachipy import dictionary, tokenizer as sudachi_tokenizer

tokenizer_obj = dictionary.Dictionary().create()
mode = sudachi_tokenizer.Tokenizer.SplitMode.C


def analyze_text(text):
    all_tokens = []

    noun_tokens = []
    verb_tokens = []
    adj_tokens = []
    adv_tokens = []

    for m in tokenizer_obj.tokenize(text, mode):
        base = m.dictionary_form()
        pos = m.part_of_speech()[0]

        # 老师要求不过滤这些常见词，所以这里不做 stopwords 过滤
        if pos in ["名詞", "動詞", "形容詞", "副詞"]:
            all_tokens.append(base)

        if pos == "名詞":
            noun_tokens.append(base)
        elif pos == "動詞":
            verb_tokens.append(base)
        elif pos == "形容詞":
            adj_tokens.append(base)
        elif pos == "副詞":
            adv_tokens.append(base)

    return {
        "all": Counter(all_tokens),
        "名詞": Counter(noun_tokens),
        "動詞": Counter(verb_tokens),
        "形容詞": Counter(adj_tokens),
        "副詞": Counter(adv_tokens),
    }
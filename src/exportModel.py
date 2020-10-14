#!/usr/bin/env python3
import MeCab
import markovify
mecabW = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd -O wakati")


def generateAndExport(src, dest, state_size=3):
    src = src.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("?", "？").replace("!", "！").replace("，", "、").replace("．", "。").replace("&quot;", "").replace("&#39;", "").replace("&nbsp;", "").replace("&apos;", "").replace("。", "。\n")
    data = [mecabW.parse(s) for s in src.split("\n") if s != ""]
    joinedData = "".join(data)
    modeljson = markovify.NewlineText(joinedData, state_size=state_size).to_json()
    with open(dest, mode="w") as f:
        f.write(modeljson)
    return len(data)

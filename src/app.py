#!/usr/bin/env python3
import configparser
import time
import threading
import mastodonTool
import os
import datetime
import markovify
import exportModel

# 環境変数の読み込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')


def worker():
    # 学習
    domain = config_ini['read']['domain']
    read_access_token = config_ini['read']['access_token']
    write_access_token = config_ini['write']['access_token']

    account_info = mastodonTool.get_account_info(domain, read_access_token)
    params = {"exclude_replies": 1, "exclude_reblogs": 1}
    filename = "{}@{}".format(account_info["username"], domain)
    filepath = os.path.join("./chainfiles", os.path.basename(filename.lower()) + ".json")
    if (os.path.isfile(filepath) and datetime.datetime.now().timestamp() - os.path.getmtime(filepath) < 60 * 60 * 24):
        print("モデルは再生成されません")
    else:
        exportModel.generateAndExport(mastodonTool.loadMastodonAPI(domain, read_access_token, account_info['id'], params), filepath)
        print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
    # 生成
    with open("./chainfiles/{}@{}.json".format(account_info["username"].lower(), domain)) as f:
        textModel = markovify.Text.from_json(f.read())
        sentence = textModel.make_sentence(tries=300)
        sentence = "".join(sentence.split()) + ' #bot'
        print(sentence)
    try:
        mastodonTool.post_toot(domain, write_access_token, {"status": sentence})
    except Exception as e:
        print("投稿エラー")


def schedule(interval, f, wait=True):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target=f)
        t.start()
        if wait:
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)


if __name__ == "__main__":
    # 定期実行部分
    schedule(1800, worker)
    # worker()

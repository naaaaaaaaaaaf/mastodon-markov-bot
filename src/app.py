#!/usr/bin/env python3
import configparser
import time
import threading
import mastodonTool
import os
import datetime
import markovify
import exportModel
import re
import s3


config_ini = configparser.ConfigParser()
is_lambda = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is not None


def worker():
    # 学習
    domain = config_ini['read']['domain']
    read_access_token = config_ini['read']['access_token']
    write_access_token = config_ini['write']['access_token']

    account_info = mastodonTool.get_account_info(domain, read_access_token)
    params = {"exclude_replies": 1, "exclude_reblogs": 1}
    base_dir = "/tmp" if is_lambda else "./chainfiles"
    filename = "{}@{}.json".format(account_info["username"], domain).lower()
    filepath = os.path.join(base_dir, os.path.basename(filename.lower()))

    if is_lambda:
        s3.get_file(filename, filepath)

    if (os.path.isfile(filepath) and datetime.datetime.now().timestamp() - os.path.getmtime(filepath) < 60 * 60 * 24):
        print("モデルは再生成されません")
    else:
        exportModel.generateAndExport(mastodonTool.loadMastodonAPI(domain, read_access_token, account_info['id'], params), filepath)
        print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log

        if is_lambda:
            s3.put_file(filename, filepath)

    # 生成
    with open(filepath) as f:
        textModel = markovify.Text.from_json(f.read())
        sentence = textModel.make_sentence(tries=300)
        sentence = "".join(sentence.split()) + ' #bot'
        sentence = re.sub(r'(:.*?:)', r' \1 ', sentence)
        print(sentence)
    try:
        mastodonTool.post_toot(domain, write_access_token, {"status": sentence})
    except Exception as e:
        print("投稿エラー: {}".format(e))


def schedule(f, interval=1200, wait=True):
    base_time = time.time()
    next_time = 0
    while True:
        t = threading.Thread(target=f)
        t.start()
        if wait:
            t.join()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)


def handler(event, context):
    config_ini.read('config.ini.sample', encoding='utf-8')
    config_ini['read']['domain'] = os.environ['DOMAIN']
    config_ini['read']['access_token'] = os.environ['READ_ACCESS_TOKEN']
    config_ini['write']['access_token'] = os.environ['WRITE_ACCESS_TOKEN']
    worker()


if __name__ == "__main__":
    # 定期実行部分
    config_ini.read('config.ini', encoding='utf-8')
    schedule(worker)
    # worker()

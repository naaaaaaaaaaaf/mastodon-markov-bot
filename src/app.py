#!/usr/bin/env python3
import configparser
import time
import threading
import mastodonTool

# 環境変数の読み込み
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')


def worker():
    # 学習 or トゥート生成
    print(time.time())
    time.sleep(8)


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
    schedule(5, worker)

#!/usr/bin/env python3
from os import access
import re
import requests
import json


def get_account_info(domain, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    res = requests.get('https://' + domain + '/api/v1/accounts/verify_credentials', headers=headers).json()
    return res


def post_toot(domain, access_token, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/statuses".format(domain)
    response = requests.post(url, headers=headers, json=params)
    if response.status_code != 200:
        raise Exception('リクエストに失敗しました。')
    return response


def filterToots(twts):
    replyMatch = re.compile(r"@\w+")
    urlMatch = re.compile(r"https?://")
    data = []
    for text in twts:
        if replyMatch.search(text) or urlMatch.search(text):
            continue
        data.append(text)
    return data


def fetchToots(domain, access_token, account_id, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/accounts/{}/statuses".format(domain, account_id)
    response = requests.get(url, headers=headers, json=params)
    if response.status_code != 200:
        raise Exception('リクエストに失敗しました。')
    return response


def fetchTootsLoop(domain, access_token, account_id, params, loop):
    toots = []
    for i in range(loop):
        try:
            req = fetchToots(domain, access_token, account_id, params)
            # print(req.status_code)
            req = req.json()
            for x in req:
                last_id = x['id']
                print(x['content'])
                if x['visibility'] == 'private' or x['visibility'] == 'direct':
                    print("鍵投稿のためスキップしました。 {}".format(x['content']))
                    continue
                seikei = re.compile(r"<[^>]*?>").sub("", x['content'])
                toots.append(seikei)
                params["max_id"] = last_id
        except Exception as e:
            print("読み込みエラー: {}".format(e))
            break
    # 重複投稿を削除
    toots = list(set(toots))
    return toots


def loadMastodonAPI(domain, access_token, account_id, params):
    toots = fetchTootsLoop(domain, access_token, account_id, params, 200)
    return "\n".join(filterToots(toots))

#!/usr/bin/env python3
import re
import requests
import json


def filterToots(twts):
    replyMatch = re.compile(r"@\w+")
    urlMatch = re.compile(r"https?://")
    data = []
    for text in twts:
        if replyMatch.search(text) or urlMatch.search(text):
            continue
        data.append(text)
    return data


def loadTootsJS(filepath):
    with open(filepath) as f:
        text = f.read()
    text = text[25:]
    data = json.loads(text)
    text = [s["tweet"]["full_text"] for s in data]
    return "\n".join(filterToots(text))


def fetchToots(domain, access_token, account_id, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/accounts/{}/statuses".format(domain, account_id)
    req = requests.get(url, headers=headers, json=params).json()
    return req


def fetchTootsLoop(domain, access_token, account_id, params, loop):
    toots = []
    for i in range(loop):
        req = fetchToots(domain, access_token, account_id, params)
        for x in req:
            last_id = x['id']
            # print(x['content'])
            if x['']:
                print("we find private toot! skip")
                continue
            seikei = re.compile(r"<[^>]*?>").sub("", x['content'])
            toots.append(seikei)
        params["max_id"] = last_id
    return toots


def loadMastodonAPI(domain, access_token, account_id, params):
    toots = fetchTootsLoop(domain, access_token, account_id, params, 100)
    return "\n".join(filterToots(toots))

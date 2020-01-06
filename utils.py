# -*- coding: utf-8 -*-
import os
import json

cookie_path = "./cookies/cookies.txt"
html_path = "./cookies/"
def save_cookies(cookies):
    with open(cookie_path,'w') as w:
        json.dump(cookies,w)

def load_cookies():
    if not os.path.exists(cookie_path):
        return ""
    with open(cookie_path,'r') as r:
        return json.loads(r.read())

def save_html(key,page):
    with open( html_path + key,'wb') as wb:
        wb.write(page)
# -*- coding: utf-8 -*-
# @File    : session.py
# @Time    : 2024/12/31 13:14
# @Author  : Meteor
# @Blog    : https://www.cnblogs.com/pigke


import time
import json

import random
import string
from urllib.parse import quote, urlparse

import requests
from loguru import logger

from utils.crypto import AESCrypto


def _random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _generate_random_iv() -> str:
        aes_crypto = AESCrypto(key=b"E08247708934F42E", iv=b"0A234C4C639E015D")
        t = _random_string() + "-" + _random_string() + str(int(time.time() * 1000))
        iv = aes_crypto.aes_encrypt(content=t).replace("_", "")[0:16]
        return iv


class Session:
    def __init__(self):
        iv = _generate_random_iv()
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Content-Type": "application/json; charset=UTF-8",
            "Fetch-Mode": self.user_agent,
            "User-Agent": self.user_agent,
            "etag": iv,
        }
        self.last_server_seq_num = 0
        self.tab_id = _random_string(10)
        self.aes_crypto = AESCrypto(key=b"QaZB7ddSo0bedGhW", iv=bytes(iv, "utf-8"))

        logger.success(f"Init Success, iv: {iv}, tabId: {self.tab_id}")


    def get(self, url: str):
        cid = _random_string()
        # 解析URL
        parsed_url = urlparse(url)
        url_prefix = f"{parsed_url.scheme}://{parsed_url.netloc}"
        uuid = "3147b8ad-de27-43de-86d6-220e7fb373bc"
        data = {
            "uuid": uuid,
            "url": url,
            "cid": cid,
            "_": self.user_agent + "|" + cid,
            "common": {
                "isPost": False,
                "postBody": "",
                "userAgent": self.user_agent,
                "platform": "Win32",
                "language": "zh-CN",
                "languages": "zh-CN,en,en-GB,en-US",
                "timeZone": "Asia/Shanghai",
                "tabId": self.tab_id,
                "referrer": "",
                "isReload": True,
                "docType": "<!DOCTYPE html>",
                "screenWidth": 1920,
                "screenHeight": 1080,
                "windowWidth": 1920,
                "windowHeight": 1004,
                "isMobile": False,
                "urlPrefix": url_prefix + "/1ywuKELSO2ahQuWZ/pr/0",
                "cookies": None,
                "zoomFactor": 100,
            },
            "extension": {"reuse": False, "simMode": False},
        }

        payload = json.dumps(data)
        data = {"data": self.aes_crypto.aes_encrypt(content=payload)}
        logger.info(f"data: {data}")
        session_url = url_prefix + "/1ywuKELSO2ahQuWZ/api/v1/sessions"
        response = requests.post(
            session_url, headers=self.headers, json=data, verify=False
        )
        logger.info(
            f"session status_code: {response.status_code}, response: {response.text}"
        )
        # 解析加密数据
        decrypted = (
            self.aes_crypto.aes_decrypt(response.json()["data"]).rsplit("}", 1)[0] + "}"
        )
        resp_data = json.loads(decrypted)
        logger.info(f"response data: {resp_data}")
        token = quote(resp_data["token"].replace("/", "_"), safe="")
        uuid = resp_data["uuid"]

        return {
             'url_prefix': url_prefix,
             'token': token,
             'tab_id': self.tab_id,
             'uuid': uuid
        }

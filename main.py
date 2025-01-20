# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2024/12/31 13:14
# @Author  : Meteor
# @Blog    : https://www.cnblogs.com/pigke


import time

import msgpack
import websocket
from loguru import logger
from pyquery import PyQuery

from utils.parser import Parser
from utils.session import Session
from utils.converter import Converter


class WebsocketSpider:
    def __init__(self, url: str, version: int = 1):
        self.url = url
        self.version = version

        self.urls = []
        self.local_seq_num = 0
        self.open_type = "new-window"

        self.session = Session()
        self.ws = websocket.WebSocket()
        self.parser = Parser(on_navigate=self.on_navigate)

    def generate_ws_url(self):
        data = self.session.get(self.url)
        # 生成websockt链接
        ws_prefix = data["url_prefix"].replace("http", "ws")
        ws_url = f"{ws_prefix}/1ywuKELSO2ahQuWZ/pr/{data['token']}/b/ws/{data['tab_id']}/{data['uuid']}"
        logger.success(f"websocket url: {ws_url}")

        return ws_url

    def pack_msg(self, cmd: list):
        cmd.insert(0, self.session.tab_id)
        _type = "1"
        if cmd[2] == "browseraction":
            _type = ""
        cmd.insert(1, _type)
        self.local_seq_num += 1
        return msgpack.packb([self.local_seq_num, cmd])

    def click_link(self, nid: str):
        """
        点击超链接事件
        """
        mouse_obj = {
                "commandCode": 4,
                "fid": "1",
                "nid": nid,
                "type": "mousedown",
                "elementX": 0,
                "elementY": 0,
                "detail": 1,
                "button": 0,
                "buttons": 1,
                "modifiers": 0,
                "relNid": "",
                "screenX": 0,
                "screenY": 0,
                "movementX": 0,
                "movementY": 0,
                "offsetX": 0,
                "offsetY": 0,
                "pageX": 0,
                "pageY": 0,
                "x": 0,
                "y": 0,
                "composed": True,
            }
        
        click_obj = {
                "commandCode": 4,
                "fid": "1",
                "nid": nid,
                "type": "click",
                "elementX": 0,
                "elementY": 0,
                "detail": 1,
                "button": 0,
                "buttons": 0,
                "modifiers": 0,
                "relNid": "",
                "screenX": 0,
                "screenY": 0,
                "movementX": 0,
                "movementY": 0,
                "offsetX": 0,
                "offsetY": 0,
                "pageX": 0,
                "pageY": 0,
                "x": 0,
                "y": 0,
                "composed": True,
            }
        

        if self.version == 1:  # 版本1结构，参考颍东先锋网
            mouse_obj.update(
                {
                    "offsetNid": "0",
                    "scrollNid": "0",
                    "scrollTop": 0,
                    "scrollLeft": 0
                }
            )
        elif self.version == 2:  # 版本2结构，参考陕西财政
            mouse_obj.update(
                {
                    "region": "",
                    "mozPressure": "",
                    "mozInputSource": "",
                    "webkitForce": "",
                    "clientX": 0,
                    "clientY": 0
                }
            )
            click_obj.update(
                {
                    "region": "",
                    "mozPressure": "",
                    "mozInputSource": "",
                    "webkitForce": "",
                    "clientX": 0,
                    "clientY": 0
                }
            )
        else:
            raise ValueError("version must be 1 or 2")

        mouse_cmd = Converter.converter_command_mouse(mouse_obj)
        self.ws.send_bytes(self.pack_msg(mouse_cmd))

        click_cmd = Converter.converter_command_click(click_obj)
        self.ws.send_bytes(self.pack_msg(click_cmd))
        logger.info("already click.")

    def get_article_url(self, lx_id: str):
        self.click_link(lx_id)
        self.recv_msg()

        if self.open_type == "new-window":
            # todo 新窗口打开
            ...
        elif self.open_type == "navigate":
            # 在当前页面跳转，需要使用后退事件返回列表页
            html = self.parser.render_html()
            self.save_html_local("article", html)
            logger.info(self.urls)

            self.parser.command_queue = []
            browser_action_cmd = Converter.converter_command_browser_action(
                {
                    "commandCode": 0,
                    "opsCode": "browseraction",
                    "action": -1,
                    "url": self.url,
                    "cookies": None,
                    "isPost": False,
                    "isMobile": False,
                    "zoomFactor": 1,
                    "dpr": 1,
                    "postBody": "",
                    "width": 1619,
                    "height": 1004,
                }
            )
            self.parser.command_queue = []
            self.ws.send_bytes(self.pack_msg(browser_action_cmd))
            self.recv_msg()

    def recv_msg(self):
        while True:
            message = self.ws.recv()
            if not message:
                break
            result = msgpack.unpackb(message)
            if self.parser.parse_msg(result):
                break

    def on_navigate(self, cmd: list):
        logger.warning(f"On navigate, {cmd}")
        self.open_type = "navigate"
        if self.url != cmd["url"]:
            self.urls.append(cmd["url"])  # 存储详情页链接

    @staticmethod
    def save_html_local(filename: str, html: str):
        with open(f"./output/{filename}.html", "w", encoding="utf-8") as f:
            f.write(html)
            logger.success("Save html success.")

    def run(self, selector: str = "*"):
        ws_url = self.generate_ws_url()
        self.ws.connect(ws_url)
        self.recv_msg()

        html = self.parser.render_html()
        self.save_html_local("index", html)

        doc = PyQuery(html)
        logger.info(f"Found {len(doc(selector))} links.")
        for a in doc(selector):
            print(a.attrib["lx-id"], a.attrib.get("href"), a.text)
            self.get_article_url(a.attrib["lx-id"].split("_")[1])
            break

        print(len(self.parser.command_queue))


if __name__ == "__main__":
    # 示例网站
    webiste_list = [
        {
            "url": "https://www.ydxf.gov.cn/News/showList/4/page_1.html",
            "version": 1,
            "list_css": ".list-switch a"
        }, {
            "url": "http://czt.shaanxi.gov.cn/xxgk/rsxx1221.chtml?id=Q7J7Jf&p=1",
            "version": 2,
            "list_css": ".detailed-text a"
        }
    ]
    ws_spider = WebsocketSpider(url=webiste_list[0]['url'], version=webiste_list[0]['version'])
    ws_spider.run(webiste_list[0]['list_css'])
    logger.success(f"Finished, cost:{time.perf_counter()}s")

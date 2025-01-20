# -*- coding: utf-8 -*-
# @File    : parser.py
# @Time    : 2024/12/31 13:14
# @Author  : Meteor
# @Blog    : https://www.cnblogs.com/pigke


from typing import Optional, Callable

from loguru import logger
from pyquery import PyQuery

from utils.converter import Converter


class Parser:
    """
    解析器
    """

    def __init__(self, on_navigate: Optional[Callable] = None):
        self.on_navigate = on_navigate

        # 命令处理器
        self.command_handlers = {
            '0-newwindow': Converter.converter_object_new_window,
            '0-browseraction': Converter.converter_object_browser_action,
            '8': Converter.converter_object_tag,
            '16': Converter.converter_object_text,
            '31': Converter.converter_object_navigate,
            '55': Converter.converter_object_multi_cmd
        }
        self.urls = []
        self.command_queue = []
        self.max_seq_num = 4
        self.last_server_seq_num = 0

    def parse_msg(self, msgs: list):
        for msg in msgs:
            r = msg[0]
            if not msg[1]:
                logger.error(f"Invalid message, {msg}")
                continue
            if msg[1][1] == 32:
                logger.info(f"CommandCode SYNC, {msg}")
                if self.last_server_seq_num > self.max_seq_num:
                    self.max_seq_num = self.last_server_seq_num + 4
                    return True
                return
            if r == -1:
                logger.error(f"Error message, {msg}")
                continue
            if (
                1 == r
                or 0 == self.last_server_seq_num
                or r == self.last_server_seq_num + 1
            ):
                self.last_server_seq_num = r
                self.on_receive(msg[1])

    def on_receive(self, e):
        """
        接收指令
        """
        # n = e[0]
        i = e[1:]
        obj = self.convert_cmd_to_obj(i)
        if not obj:
            return
        self.convert_cmd(obj)

    def convert_cmd_to_obj(self, cmd: list) -> dict:
        """
        解析单条指令
        """
        command_code = cmd[0]
        # 处理commandCode为0的情况
        if command_code == 0:
            command_code = "0-" + cmd[1].replace('-', '')
        handler = self.command_handlers.get(str(command_code))
        if not handler:
            logger.error(f"Unknown command code, {command_code}, {cmd}", )
            return {}
        obj = handler(cmd)
        return obj

    def convert_cmd(self, cmd: dict):
        """
        递归转换指令，主要用于处理一条指令内含有多条其它指令
        """
        if cmd['commandCode'] == 55:  # MultiCmd
            for t in cmd['content']:
                c = self.convert_cmd_to_obj(t)
                if not c:
                    continue
                self.convert_cmd(c)
        if cmd['commandCode'] == 31:
            self.command_queue = []
            self.on_navigate and self.on_navigate(cmd)
        else:
            self.command_queue.append(cmd)

    def render_html(self):
        """
        还原html
        """
        logger.success(self.command_queue[: 6])
        if not self.command_queue:
            return
        # 根据nid排序
        # command_queue.sort(key=lambda x: int(x.get('nid')))

        doc = PyQuery('<html></html>')
        for cmd in self.command_queue:
            # logger.warning(cmd)
            # 过滤style标签
            if cmd.get('tag') in ['style', 'iframe']:
                continue

            # html初始化
            if cmd.get('commandCode') == 8 and cmd.get('parent') is None:
                doc('html').attr('lx-id', f"lx_{cmd.get('nid')}")
                logger.info(f'insert tag {cmd.get("tag")} {cmd.get("nid")}')
                continue
            else:  # 根据parent找出父节点
                # p_element = doc(f"#lx_{cmd.get('parent')}")
                p_element = doc(f'*[lx-id="lx_{cmd.get("parent")}"]')
                if not p_element:
                    logger.error(f"Not find parent element, {cmd}")
                    continue
            if cmd.get('commandCode') == 8:  # tag
                attrs = []
                for attr in cmd['attributes']:
                    tag_name = attr['name']
                    tag_value = attr['value']
                    attrs.append(f'{tag_name}="{tag_value}"')
                p_element.append(f'<{cmd.get("tag")} lx-id="lx_{cmd.get("nid")}" {" ".join(attrs)}></{cmd.get("tag")}>')
                logger.debug(f'Insert tag <{cmd.get("tag")}> {cmd.get("nid")} to {cmd.get("parent")}')
            elif cmd.get('commandCode') == 16:  # text
                # 过滤style和script标签
                if p_element[0].tag in ['style', 'script']:
                    continue
                p_element.append(cmd.get('textContent'))
                # 忽略空文本
                if cmd.get("textContent", "").strip():
                    logger.debug(f'Fill text {cmd.get("textContent")} {cmd.get("nid")} to {cmd.get("parent")}')
        # logger.success(doc.outer_html())
        return doc.outer_html()

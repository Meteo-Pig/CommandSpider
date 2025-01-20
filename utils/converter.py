# -*- coding: utf-8 -*-
# @File    : converter.py
# @Time    : 2024/12/31 13:14
# @Author  : Meteor
# @Blog    : https://www.cnblogs.com/pigke


from urllib.parse import unquote

from loguru import logger


class Converter:
    """
    指令转换器
    """

    @staticmethod
    def converter_command_mouse(e):
        attrs = ['commandCode', 'fid', 'nid', 'type', 'elementX', 'elementY', 'detail', 'button', 'buttons',
                 'modifiers', 'relNid', 'screenX', 'screenY', 'movementX', 'movementY', 'offsetX', 'offsetY',
                 'offsetNid', 'pageX', 'pageY', 'region', 'mozPressure', 'mozInputSource', 'webkitForce', 'x', 'y', 
                 'clientX', 'clientY', 'composed', 'scrollNid', 'scrollLeft', 'scrollTop']
        result = []
        for attr in attrs:
            _attr = e.get(attr)
            if _attr is not None:
                result.append(_attr)
        return result

    @staticmethod
    def converter_command_click(e):
        attrs = ['commandCode', 'fid', 'nid', 'type', 'elementX', 'elementY', 'detail', 'button', 'buttons',
                 'modifiers', 'relNid', 'screenX', 'screenY', 'movementX', 'movementY', 'offsetX', 'offsetY',
                 'pageX', 'pageY', 'region', 'mozPressure', 'mozInputSource', 'webkitForce', 'x', 'y', 
                 'clientX', 'clientY', 'composed']
        result = []
        for attr in attrs:
            _attr = e.get(attr)
            if _attr is not None:
                result.append(_attr)
        return result

    @staticmethod
    def converter_command_modify_attr(e):
        attrs = ['commandCode', 'fid', 'nid', 'name', 'value']
        result = []
        if e is not None:
            for attr in attrs:
                result.append(e.get(attr))
        return result

    @staticmethod
    def converter_object_multi_cmd(t):
        if len(t) != 4:
            logger.error("MultiCmdMessageConverter#converterToObject The message length is wrong, "
                         "expectation is 4, the actual is", len(t))
            return None

        return {
            'commandCode': t[0],
            'content': t[1],
            'first': t[2],
            'config': t[3]
        }

    @staticmethod
    def converter_object_new_window(t):
        if len(t) != 6:
            logger.error("NewWindowMessageConverter#converterToObject The message length is wrong, "
                         "expectation is 6, the actual is", len(t))
            return None

        return {
            'commandCode': t[0],
            'opsCode': t[1],
            'tabId': t[2],
            'showUrl': t[3],
            'clearNewWindowTimeout': t[4],
            'openWinPopupConfirmDialog': t[5]
        }

    @staticmethod
    def converter_object_browser_action(t):
        if len(t) != 12:
            logger.error("BrowserActionTabOpsMessageConverter#converterToObject The message length is wrong, "
                         "expectation is 12, the actual is", len(t))
            return None

        return {
            'commandCode': t[0],
            'opsCode': t[1],
            'action': t[2],
            'url': t[3],
            'cookies': t[4],
            'isPost': t[5],
            'width': t[6],
            'height': t[7],
            'isMobile': t[8],
            'zoomFactor': t[9],
            'dpr': t[10],
            'postBody': t[11]
        }
    
    @staticmethod
    def converter_command_browser_action(e):
        attrs = ['commandCode', 'opsCode', 'action', 'url', 'cookies', 'isPost', 'isMobile', 'zoomFactor', 'dpr', 'postBody', 'width', 'height']
        result = []
        if e is not None:
            for attr in attrs:
                result.append(e.get(attr))
        return result

    @staticmethod
    def converter_object_navigate(t):
        if not (len(t) == 6 or len(t) == 8):
            logger.error("NavigateMessageConverter#converterToObject The message length is wrong, "
                         "expectation is 6 or 8, the actual is", len(t))
            return None

        if len(t) == 6:
            return {
                'commandCode': t[0],
                'fid': t[1],
                'url': t[2],
                'reload': t[3],
                'state': t[4],
                'isPost': t[5]
            }
        return {
            'commandCode': t[0],
            'fid': t[1],
            'url': t[2],
            'reload': t[3],
            'state': t[4],
            'hashMode': t[5],
            'isPost': t[6],
            'hashHistorySplit': t[7]
        }

    @staticmethod
    def converter_object_text(t):
        if len(t) != 8:
            logger.error("AddElementMessageConverter#converterToObject The message length is wrong, "
                         "expectation is 8, the actual is", len(t))
            return None

        return {
            'commandCode': t[0],
            'fid': t[1],
            'nid': t[2],
            'tag': t[3],
            'textContent': unquote(t[4]),
            'parent': t[5],
            'previousSiblingNid': t[6],
            'hasChild': t[7]
        }

    @staticmethod
    def converter_object_tag(t):
        if len(t) != 11:
            logger.error("AddElementMessageConverter#converterToObject The message length is wrong, "
                         "expectation is 11, the actual is", len(t))
            return None

        e = {
            'commandCode': t[0],
            'fid': t[1],
            'nid': t[2],
            'tag': t[3],
            'attributes': [],
            'properties': [],
            'parent': t[6],
            'previousSiblingNid': t[7],
            'shadowRoot': t[8],
            'hasChildNodes': t[9],
            'fullPageMedia': t[10]
        }

        for attr in t[4]:
            e['attributes'].append({
                'name': attr[0],
                'value': attr[1],
                'namespaceURI': attr[2]
            })

        for prop in t[5]:
            e['properties'].append({
                'name': prop[0],
                'value': prop[1]
            })

        return e

#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# @Author   : chuanwen.peng
# @Time     : 2022/4/15 14:21
# @File     : yaml_parser.py
# @Project  : Glass_UI
"""
import yaml


class ReadYaml:
    """ 读取yaml数据的类 """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(ReadYaml, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def read(self, path):
        with open(path, encoding="utf-8") as f:
            result = f.read()
            result = yaml.load(result, Loader=yaml.FullLoader)
            return result

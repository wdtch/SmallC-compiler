#!/usr/bin/python
# -*- coding: utf-8 -*-

"""意味解析モジュール"""

from __future__ import unicode_literals

class Decl(object):
    def __init__(self, name, level, kind, objtype):
        self.name = name
        self.level = level
        self.kind = kind
        self.type = objtype

class Environment(Decl):
    def __init__(self, decl=None):
        if decl is None:
            self.decl_list = []
        else:
            self.decl_list = [decl]

    def add(self, decl):
        self.decl_list.append(decl)

    def is_found(self, name):
        for i in range(len(decl_list)):
            if name == decl_list[i].name:
                return True
            else:
                if i == len(decl_list-1):
                    return False
                else:
                    pass

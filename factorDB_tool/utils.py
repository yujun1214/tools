#!/usr/bin/env/ python3
# -*- coding: utf-8 -*-
# @Abstract: 
# @Filename: utils
# @Date:   : 2018-01-16 20:48
# @Author  : YuJun
# @Email   : yujun_mail@163.com


def code_to_symbol(code):
    """
    生成本系统的证券代码symbol
    Parameters:
    --------
    :param code: str
        原始代码，如600000
    :return: str
        本系统证券代码，如SH600000
    """
    if len(code) != 6:
        return code
    else:
        return 'SH%s' % code if code[:1] in ['5', '6', '9'] else 'SZ%s' % code


if __name__ == '__main__':
    pass

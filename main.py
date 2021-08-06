#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hkpic import HKPIC
import sys
import json
from common import save_log, today_in_log, local_time, weixin_openid


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()

    time = local_time().strftime('%Y-%m-%d %H:%M:%S')
    print(f'\n当前北京时间：{time}\n')

    jsonValue = json.loads(sys.argv[1])
    # 读取并设置微信openid（功能暂时没用）
    weixin_openid(jsonValue)

    # 广东移动App签到
    if not today_in_log():
        save_log(local_time().date())

    hkpicValue = jsonValue['HKPIC']
    accounts = hkpicValue["accounts"]
    hkpicValue.pop('accounts')

    # 比思签到+赚取每日金币(多账号)
    for (id, account) in enumerate(accounts):
        dic = {**hkpicValue, **account}
        hkpic = HKPIC(dic, (id + 1))
        print(f'------------- {hkpic.username} 比思签到 -------------')
        hkpic.runAction()
        print(f'------------- {hkpic.username} 比思签到完成 -------------')

#!/usr/bin/python3
# -*- coding: utf-8 -*-

from hkpic import HKPIC
from common import local_time, weixin_openid
import sys
import json
import time


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit()

    ltime = local_time().strftime('%Y-%m-%d %H:%M:%S')
    print(f'\n当前北京时间：{ltime}\n')

    jsonValue = json.loads(sys.argv[1])
    # 读取并设置微信openid（功能暂时没用）
    weixin_openid(jsonValue)

    hkpicValue = jsonValue['HKPIC']
    accounts = hkpicValue["accounts"]
    hkpicValue.pop('accounts')

    total_time = 0
    # 比思签到+赚取每日金币(多账号)
    for account in accounts:
        start = time.time()
        dic = {**hkpicValue, **account}
        hkpic = HKPIC(dic)
        print(f'------------- {hkpic.nickname} 比思签到 -------------')
        hkpic.runAction()
        s = time.time() - start
        min = int(s/60)
        if min > 0:
            consume = '%d分%.0f秒' % (min, s - min*60)
        else:
            consume = f'{"%.2f" % s}秒'
        print(f'------------- 签到完成,耗时{consume} -------------')
        total_time += s
        '''
            github的Action最长执行时间为60分钟，一个账号所需要时间为25分钟左右。
            如果执行时行达到35分钟，就不再执行。下一次执行剩下的账号。
            可以通过配置Action的循环执行时间，一天最多可以执行24次。
        '''
        if total_time > 2100:
            break

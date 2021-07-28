#!/usr/bin/python3
# -*- coding: utf-8 -*-

from html import unescape
from urllib.parse import unquote
import ctypes
import random
import os
import sys
import random
import string
import requests
import json
import base64

all_cookies = {}

# 获取运行目录
def get_running_path(path=''):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), path)
    elif __file__:
        return os.path.join(os.path.dirname(__file__), path)


def random_string(randomlength=32):
    """
    生成一个指定长度的随机字符串，其中
    string.digits=0123456789
    string.ascii_lowercase=abcdefghigklmnopqrstuvwxyz
    """
    str_list = [random.choice(string.digits + string.ascii_lowercase) for i in range(randomlength)]
    random_str = ''.join(str_list)
    return random_str


def random_num_string(randomlength=32):
    ''' 生成随机纯数字字符串 '''
    str_list = [random.choice(string.digits) for i in range(randomlength)]
    # 去掉前面的0
    while len(str_list) > 0:
        if str_list[0] == '0':
            str_list.pop(0)
        else:
            break

    # 补齐长度
    count = len(str_list)
    if count < randomlength:
        str_list += random_num_string(randomlength-count)
    random_str = ''.join(str_list)
    return random_str


# 保存内容到readme中
def save_readme(texts):
    fold = os.path.abspath('.')
    readMePath = os.path.join(fold, "README.md")
    with open(readMePath, 'a+') as f:
        f.seek(0)
        f.write('  \n')
        f.write('  \n'.join(texts))
        f.flush()


def get_access_token():
    """
    获取微信全局接口的凭证(默认有效期俩个小时)
    如果不每天请求次数过多, 通过设置缓存即可
    """
    result = requests.get(
        url="https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": "wxc4ab4341d9a8577a",
            "secret": "e6c46e8cc24a95df1742ff8b25aaf36b",
        }
    ).json()

    if result.get("access_token"):
        access_token = result.get('access_token')
    else:
        access_token = None
    return access_token


def weixin_send_msg(msg, openid):
    access_token = get_access_token()

    all_msg = []
    if type(msg) is str:
        all_msg.append(msg)
    elif type(msg) is list:
        all_msg += msg
    else:
        return

    body = {
        "touser": openid,
        "msgtype": "text",
        "text": {
            "content": ' '.join(msg)
        }
    }
    response = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
        params={
            'access_token': access_token
        },
        data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
    )
    # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
    result = response.json()
    print(result)
    all_msg.append(json.dumps(result))
    save_readme(all_msg)


# 保存文件
def save_file(name, text):
    path = get_running_path(name)
    with open(path, 'a+') as f:
        f.write(text)
        f.flush()


# 读取相应的cookie
def load_cookies(key, xor_key):
    path = get_running_path('cookies.txt')
    if not os.path.exists(path):
        return ''
    global all_cookies
    if not all_cookies:
        with open(path, 'r') as f:
            jsonData = f.read()
            if jsonData:
                all_cookies = json.loads(jsonData)
    if key in all_cookies.keys():
        value = all_cookies[key]
    else:
        return {}
    if value:
        try:
            s = xor(value, xor_key, False)
            return json.loads(s)
        except ValueError:
            return {}
    else:
        return {}


# 写入cookie
def save_cookies(key, xor_key, cookies):
    path = get_running_path('cookies.txt')
    global all_cookies
    all_cookies[key] = xor(cookies, xor_key, True)
    with open(path, 'w') as f:
        f.write(json.dumps(all_cookies))   # 重写数据
        f.flush()


def xor(text, key, encrty):
    if not encrty:
        text = str(base64.b64decode(text), "utf-8")
    ml = len(text)
    kl = len(key)
    result = []
    #通过取整，求余的方法重新得到key
    for i in range(ml):
        #一对一异或操作，得到结果,其中,"ord(char)"得到该字符对应的ASCII码,"chr(int)"刚好相反
        result.append(chr(ord(key[i % kl])^ord(text[i])))
    result = ''.join(result)
    if encrty:
        result = str(base64.b64encode(result.encode("utf-8")), "utf-8")
    return result


def int_overflow(val):
    maxint = 2147483647
    if not -maxint-1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def left_shift(n, i):
    # print('n:{}, i:{}'.format(n, i))
    # 数字左移
    v = n << i
    # 将值强转成32位整型，因为js是这样，照搬
    a = ctypes.c_int32(v).value
    return a


def unsigned_right_shitf(n, i):
    # 转为32位无符号uint
    n = ctypes.c_uint32(n).value
    # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
    if i < 0:
        return -int_overflow(n << abs(i))

    v = int_overflow(n >> i)
    if v == 0:
        return n
    else:
        return ctypes.c_uint32(v).value


def p(t, e, n, r, i, o, a):
    s = t + (e & n | ~e & r) + unsigned_right_shitf(i, 0) + a
    return (left_shift(s, o) | unsigned_right_shitf(s, 32 - o)) + e


def vv(t, e, n, r, i, o, a):
    s = t + (e & r | n & ~r) + unsigned_right_shitf(i, 0) + a
    return (left_shift(s, o) | unsigned_right_shitf(s, 32 - o)) + e


def g(t, e, n, r, i, o, a):
    s = t + (e ^ n ^ r) + unsigned_right_shitf(i, 0) + a
    return (left_shift(s, o) | unsigned_right_shitf(s, 32 - o)) + e


def m(t, e, n, r, i, o, a):
    s = t + (n ^ (e | ~r)) + unsigned_right_shitf(i, 0) + a
    return (left_shift(s, o) | unsigned_right_shitf(s, 32 - o)) + e


def rotl(t, e):
    return left_shift(t, e) | unsigned_right_shitf(t, 32 - e)


def endian(t):
    if type(t) is list:
        for e in range(0, len(t)):
            t[e] = endian(t[e])
        return t

    a = 16711935 & rotl(t, 8)
    b = 4278255360 & rotl(t, 24)

    v = ctypes.c_int32(a).value | ctypes.c_int32(b).value
    return v


def stringToBytes(t):
    v = unescape(unquote(t))
    count = len(v)
    e = []
    for i in range(0, count):
        e.append(255 & ord(v[i]))
    return e


def bytesToWords(t):
    e = []

    count = len(t)
    r = 0
    for n in range(0, count):
        i = r >> 5

        if i >= len(e):
            e.append(0)

        e[i] |= t[n] << 24 - r % 32
        r += 8
    return e


def wordsToBytes(t):
    e = []
    count = 32 * len(t)
    n = 0
    while n < count:
        a = n >> 5
        # print(n >> 5)
        # print(unsigned_right_shitf(n, 5))
        b = unsigned_right_shitf(t[a], 24 - n % 32)
        c = b & 255
        e.append(c)
        n += 8
    return e


def bytesToHex(t):
    e = []
    for n in range(0, len(t)):
        e.append('{:01X}'.format(t[n] >> 4))
        e.append('{:01X}'.format(15 & t[n]))

    return ''.join(e)


def getValue(s, i):
    if i >= len(s):
        return 0
    return s[i]


def sign(value):
    ''' 生成签名 '''
    t = stringToBytes(value)
    s = bytesToWords(t)

    t_count = 8 * len(t)

    u = 1732584193
    c = -271733879
    f = -1732584194
    d = 271733878
    for h in range(0, len(s)):
        s[h] = 16711935 & (s[h] << 8 | unsigned_right_shitf(s[h], 24)) | 4278255360 & (s[h] << 24 | unsigned_right_shitf(s[h], 8))

    index = t_count >> 5

    if index >= len(s):
        for _ in range(len(s), index+1):
            s.append(0)

    s[index] |= 128 << t_count % 32

    index = 14 + (t_count + 64 >> 9 << 4)
    if index >= len(s):
        for _ in range(len(s), index+1):
            s.append(0)
    s[index] = t_count

    h = 0
    while h < len(s):
        y = u
        b = c
        w = f
        x = d

        u = p(u, c, f, d, getValue(s, h + 0), 7, -680876936)
        d = p(d, u, c, f, getValue(s, h + 1), 12, -389564586)
        f = p(f, d, u, c, getValue(s, h + 2), 17, 606105819)
        c = p(c, f, d, u, getValue(s, h + 3), 22, -1044525330)
        u = p(u, c, f, d, getValue(s, h + 4), 7, -176418897)
        d = p(d, u, c, f, getValue(s, h + 5), 12, 1200080426)
        f = p(f, d, u, c, getValue(s, h + 6), 17, -1473231341)
        c = p(c, f, d, u, getValue(s, h + 7), 22, -45705983)
        u = p(u, c, f, d, getValue(s, h + 8), 7, 1770035416)
        d = p(d, u, c, f, getValue(s, h + 9), 12, -1958414417)
        f = p(f, d, u, c, getValue(s, h + 10), 17, -42063)
        c = p(c, f, d, u, getValue(s, h + 11), 22, -1990404162)
        u = p(u, c, f, d, getValue(s, h + 12), 7, 1804603682)
        d = p(d, u, c, f, getValue(s, h + 13), 12, -40341101)
        f = p(f, d, u, c, getValue(s, h + 14), 17, -1502002290)
        c = p(c, f, d, u, getValue(s, h + 15), 22, 1236535329)
        u = vv(u, c, f, d, getValue(s, h + 1), 5, -165796510)
        d = vv(d, u, c, f, getValue(s, h + 6), 9, -1069501632)
        f = vv(f, d, u, c, getValue(s, h + 11), 14, 643717713)
        c = vv(c, f, d, u, getValue(s, h + 0), 20, -373897302)
        u = vv(u, c, f, d, getValue(s, h + 5), 5, -701558691)
        d = vv(d, u, c, f, getValue(s, h + 10), 9, 38016083)
        f = vv(f, d, u, c, getValue(s, h + 15), 14, -660478335)
        c = vv(c, f, d, u, getValue(s, h + 4), 20, -405537848)
        u = vv(u, c, f, d, getValue(s, h + 9), 5, 568446438)
        d = vv(d, u, c, f, getValue(s, h + 14), 9, -1019803690)
        f = vv(f, d, u, c, getValue(s, h + 3), 14, -187363961)
        c = vv(c, f, d, u, getValue(s, h + 8), 20, 1163531501)
        u = vv(u, c, f, d, getValue(s, h + 13), 5, -1444681467)
        d = vv(d, u, c, f, getValue(s, h + 2), 9, -51403784)
        f = vv(f, d, u, c, getValue(s, h + 7), 14, 1735328473)
        c = vv(c, f, d, u, getValue(s, h + 12), 20, -1926607734)
        u = g(u, c, f, d, getValue(s, h + 5), 4, -378558)
        d = g(d, u, c, f, getValue(s, h + 8), 11, -2022574463)
        f = g(f, d, u, c, getValue(s, h + 11), 16, 1839030562)
        c = g(c, f, d, u, getValue(s, h + 14), 23, -35309556)
        u = g(u, c, f, d, getValue(s, h + 1), 4, -1530992060)
        d = g(d, u, c, f, getValue(s, h + 4), 11, 1272893353)
        f = g(f, d, u, c, getValue(s, h + 7), 16, -155497632)
        c = g(c, f, d, u, getValue(s, h + 10), 23, -1094730640)
        u = g(u, c, f, d, getValue(s, h + 13), 4, 681279174)
        d = g(d, u, c, f, getValue(s, h + 0), 11, -358537222)
        f = g(f, d, u, c, getValue(s, h + 3), 16, -722521979)
        c = g(c, f, d, u, getValue(s, h + 6), 23, 76029189)
        u = g(u, c, f, d, getValue(s, h + 9), 4, -640364487)
        d = g(d, u, c, f, getValue(s, h + 12), 11, -421815835)
        f = g(f, d, u, c, getValue(s, h + 15), 16, 530742520)
        c = g(c, f, d, u, getValue(s, h + 2), 23, -995338651)
        u = m(u, c, f, d, getValue(s, h + 0), 6, -198630844)
        d = m(d, u, c, f, getValue(s, h + 7), 10, 1126891415)
        f = m(f, d, u, c, getValue(s, h + 14), 15, -1416354905)
        c = m(c, f, d, u, getValue(s, h + 5), 21, -57434055)
        u = m(u, c, f, d, getValue(s, h + 12), 6, 1700485571)
        d = m(d, u, c, f, getValue(s, h + 3), 10, -1894986606)
        f = m(f, d, u, c, getValue(s, h + 10), 15, -1051523)
        c = m(c, f, d, u, getValue(s, h + 1), 21, -2054922799)
        u = m(u, c, f, d, getValue(s, h + 8), 6, 1873313359)
        d = m(d, u, c, f, getValue(s, h + 15), 10, -30611744)
        f = m(f, d, u, c, getValue(s, h + 6), 15, -1560198380)
        c = m(c, f, d, u, getValue(s, h + 13), 21, 1309151649)
        u = m(u, c, f, d, getValue(s, h + 4), 6, -145523070)
        d = m(d, u, c, f, getValue(s, h + 11), 10, -1120210379)
        f = m(f, d, u, c, getValue(s, h + 2), 15, 718787259)
        c = m(c, f, d, u, getValue(s, h + 9), 21, -343485551)
        u = unsigned_right_shitf(u + y, 0)
        c = unsigned_right_shitf(c + b, 0)
        f = unsigned_right_shitf(f + w, 0)
        d = unsigned_right_shitf(d + x, 0)
        h += 16

    r = wordsToBytes(endian([u, c, f, d]))
    return bytesToHex(r)

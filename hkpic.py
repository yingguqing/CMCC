#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 比思每日签到

from network import Network
from common import print_sleep, save_log, valueForKey, random_all_string
from bs4 import BeautifulSoup
import re
import base64
from urllib.parse import quote
from random import choice, randint
import time
from config import HKpicConfig


class HKPIC(Network):

    def __init__(self, jsonValue, id):
        super().__init__(jsonValue)
        self.all_host = [self.host]
        self.index = 0
        self.username = valueForKey(jsonValue, 'username')
        self.password = quote(valueForKey(jsonValue, 'password', default=''))
        self.config = HKpicConfig(id)
        # cookie保存到本地的Key
        self.cookies_key = 'HKPIC_COOKIES'
        # 是否需要登录
        self.is_login = False
        # 需要签到
        self.need_sign_in = True
        # 网络请求所要用到的cookie
        self.cookies = ''
        # 读取本地cookie值
        self.cookie_dit = {}
        # 别人空间地址
        self.user_href = ''
        # 自己的空间地址
        self.my_zone_url = ''
        # 自己的用户id
        self.my_uid = ''
        # 我的金币
        self.my_money = 0
        # 发表评论等所要用的
        self.formhash = ''

        # 基本的请求头，特殊情况时，在请求上使用header参数来特殊处理
        self.headers = {
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GDMobile/8.0.4',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': self.host,
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Proxy-Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': self.fullURL('forum.php')
        }
        # 帖子较多的板块
        self.all_fid = [2, 10, 11, 18, 20, 31, 42, 50, 79, 117, 123, 135, 142, 153, 239, 313, 398, 445, 454, 474, 776, 924]
        # 所有评论内容，随机使用
        self.comments = ['走过了年少，脚起了水泡。', '人生自古谁无死，啊个拉屎不用纸！', '如果跟导师讲不清楚，那么就把他搞胡涂吧！',
                         '不要在一棵树上吊死，在附近几棵树上多试试死几次。', '老天，你让夏天和冬天同房了吧？生出这鬼天气！',
                         '恋爱就是无数个饭局，结婚就是一个饭局。', '如果回帖是一种美德，那我早就成为圣人了！', '男人靠的住，母猪能上树！',
                         '天塌下来你顶着，我垫着！', '美女未抱身先走，常使色狼泪满襟。', '穿别人的鞋，走自己的路，让他们找去吧。',
                         '怀揣两块，胸怀500万！', '鸳鸳相抱何时了，鸯在一边看热闹。', '丑，但是丑的特别，也就是特别的丑！',
                         '自从我变成了狗屎，就再也没有人踩在我头上了。', '我怀疑楼主用的是金山快译且额外附带了中对中翻译。',
                         '流氓不可怕，就怕流氓有文化。', '听君一席话，省我十本书！', '如果有一双眼睛陪我一同哭泣，就值得我为生命受苦。',
                         '人生重要的不是所站的位置，而是所朝的方向！', '内练一口气，外练一口屁。', '找不到恐龙，就用蜥蜴顶。',
                         '女，喜甜食，甚胖！该女有一癖好：痛恨蚂蚁，见必杀之。问其故曰：这小东西，那么爱吃甜食，腰还那么细！',
                         '不在放荡中变坏，就在沉默中变态！', '只要不下流，我们就是主流！', '月经不仅仅是女人的痛苦，也是男人的痛苦。',
                         '佛曰，色即是空，空即是色！今晚，偶想空一下。', '勿以坑小而不灌，勿以坑大而灌之。', '读书读到抽筋处，文思方能如尿崩！',
                         '睡眠是一门艺术——谁也无法阻挡我追求艺术的脚步！', '人生不能像做菜、把所有的料都准备好才下锅！', '锻炼肌肉，防止挨揍！',
                         '我妈常说，我们家要是没有电话就不会这么穷。', '我不在江湖，但江湖中有我的传说。', '我喜欢孩子，更喜欢造孩子的过程！',
                         '时间永远是旁观者，所有的过程和结果，都需要我们自己承担。', '其实我是一个天才，可惜天妒英才！', '站的更高，尿的更远。',
                         '漏洞与补丁齐飞，蓝屏共死机一色！', '比我有才的都没我帅，比我帅的都没我有才！', '我身在江湖，江湖里却没有我得传说。',
                         '有来有往，你帮我挖坑，我买一送一，填埋加烧纸。', '所有的男人生来平等，结婚的除外。', '不在课堂上沉睡，就在酒桌上埋醉。',
                         '只有假货是真的，别的都是假的！', '男人有冲动可能是爱你，也可能是不爱，但没有冲动肯定是不爱！', '我在马路边丢了一分钱！',
                         '商女不知亡国恨、妓女不懂婚外情。', '脱了衣服我是禽兽，穿上衣服我是衣冠禽兽！', '你的丑和你的脸没有关系。',
                         '路边的野花不要，踩。', '长得真有创意，活得真有勇气！',  '走自己的路，让别人打车去吧。', '如果恐龙是人，那人是什么？'
                         '男人与女人，终究也只是欲望的动物吧！真的可以因为爱而结合吗？对不起，我也不知道。', '有事秘书干，没事干秘书！',
                         '关羽五绺长髯，风度翩翩，手提青龙偃月刀，江湖人送绰号——刀郎。', '解释就系掩饰，掩饰等于无出色，无出色不如回家休息！',
                         '俺从不写措字，但俺写通假字！', '生我之前谁是我，生我之后我是谁？', '我靠！看来医生是都疯了！要不怎么让他出院了！',
                         '勃起不是万能的，但不能勃起却是万万都不能的！', '沒有激情的亲吻，哪來床上的翻滾？', '做爱做的事，交配交的人。',
                         '有时候，你必须跌到你从未经历的谷底，才能再次站在你从未到达的高峰。', '避孕的效果：不成功，便成“人”。',
                         '与时俱进，你我共赴高潮！', '恐龙说：“遇到色狼，不慌不忙；遇到禽兽，慢慢享受。', '生，容易。活，容易。生活，不容易。',
                         '人家解释，我想，这世界上又要多我这一个疯子了。', '长大了娶唐僧做老公，能玩就玩一玩，不能玩就把他吃掉。',
                         '此地禁止大小便，违者没收工具。', '昨天，系花对我笑了一下，乐得我晚上直数羊，一只羊，两只羊，三只羊。',
                         '打破老婆终身制，实行小姨股份制。引入小姐竞争制，推广情人合同制。', '要是我灌水，就骂我“三个代表”没学好吧。']

    # 保存cookie
    def response_cookies(self, cookies):
        self.cookie_dit = {**self.cookie_dit, **cookies}

        self.cookies = ''
        values = []
        for key, value in self.cookie_dit.items():
            values.append(f'{key}={value}')
        self.cookies = '; '.join(values)

    # 开始入口
    def runAction(self):

        # 获取所有比思域名
        self.getHost()

        # 访问首页得到可用域名
        if not self.forum():
            print('没有可用域名')
            return

        print(f'域名:{self.host}')

        # 自动登录
        self.login(True)

        if not self.formhash:
            print('formhash提取失败')
            return

        # 签到
        self.signIn()
        # 评论
        self.forum_list(True)
        # 访问别人空间并留言
        self.visitUserZone()
        # 发表一条记录
        self.record()
        # 发表日志
        self.journal()
        # 删除脚本发表的日志
        self.delJournal()
        # 发表分享
        self.share()

        # 查询我的金币
        self.myMoney()
        temp = self.my_money - self.config.money
        if temp != 0:
            self.config.money = self.my_money
            self.config.save()
            save_log([f'增加：{temp}', f'金钱：{self.my_money}'])

        # 删除自己空间留言所产生的动态
        self.delAllLeavMessageDynamic()

    # 获取比思域名
    def getHost(self):
        print('获取比思域名')
        url = 'https://api.github.com/repos/hkpic-forum/hkpic/contents/README.md'

        req = self.request(url, post=False, is_save_cookies=False)
        if type(req) is dict and 'content' in req.keys():
            content = str(base64.b64decode(valueForKey(req, 'content', default='')), 'utf-8')
            if not content:
                print('获取域名失败')
                return

            pattern = re.compile(r'\b(([\w-]+://?|www[.])[^\s()<>]+(?:[\w\d]+|([^[:punct:]\s]|/)))', re.S)
            all = re.findall(pattern, content)
            for h in all:
                if type(h) is tuple and h:
                    self.all_host.append(h[0])
        else:
            print('获取域名失败')

    # 访问首页得到可用域名
    def forum(self):
        print('访问首页')

        for host in self.all_host:
            url = self.fullURL('forum.php', host)
            html = self.request(url, post=False)

            if html == '域名不通':
                print(f'{host} 请求失败，切换下一个域名')
                time.sleep(1)
                continue

            if html is not None and html.find('比思論壇') > -1:
                self.host = host
                self.headers['Origin'] = host
                self.headers['Referer'] = self.fullURL('forum.php')
                return True

        return False

    # 登录
    def login(self, show=False):
        # 需要登录时，把cookie清空
        self.cookie_dit = {}
        self.cookies = ''
        api_param = 'mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        url = self.encapsulateURL('member.php', api_param)
        # &cookietime=2592000
        params = f'fastloginfield=username&username={self.username}&password={self.password}&cookietime=2592000&quickforward=yes&handlekey=ls'
        self.request(url, params)

        url = self.fullURL('forum.php')
        html = self.request(url, post=False)
        soup = BeautifulSoup(html, 'html.parser')
        # 读取首页的用户名，如果存在，表示登录成功
        span = soup.find('a', title='訪問我的空間')
        if span:
            # 提取自己的空间地址
            self.my_zone_url = self.fullURL(span['href']) if span.has_attr('href') else ''
            self.my_uid = self.getUid(self.my_zone_url)
            self.is_login = span.text == self.username
            if self.is_login:
                self.need_sign_in = html.find('簽到領獎!') > -1
                # 提取formhash
                span = soup.find('input', attrs={'name': 'formhash'})
                if span and span.has_attr('value'):
                    self.formhash = span['value']

        if show:
            print('登录成功' if self.is_login else f'登录失败')

        if self.user_href:
            return

        # 没有别人空间地址时，提取首页随便一个人非自己的空间地址
        pattern = re.compile(r'"(space-uid-\d{5,}.html)"', re.S)
        items = re.findall(pattern, html)
        my_id = int(self.my_uid) if self.my_uid else 0
        for item in items:
            id = self.getUid(item)
            uid = int(id) if id else 0
            if not uid:
                continue

            # id比较小的应该是管理员，所以排除
            if uid > 9999 and uid != my_id:
                self.user_href = self.fullURL(item)
                break

    # 签到
    def signIn(self):

        if not self.need_sign_in:
            return

        api_param = 'id=dsu_paulsign:sign&operation=qiandao&infloat=1&sign_as=1&inajax=1'
        url = self.encapsulateURL('plugin.php', api_param)
        params = f'formhash={self.formhash}&qdxq=kx'
        html = self.request(url, params)
        pattern = re.compile(r'<div\s+class\s*=\s*"c"\s*>\W*(.*?)\W*<\s*/\s*div\s*>', re.S)
        items = re.findall(pattern, html)
        if items:
            print(items[0])
        else:
            print(f'签到失败\n{html}')

    # 版块帖子列表
    def forum_list(self, first_time=False):

        if not self.config.canReply():
            return

        # 版块id
        fid = choice(self.all_fid)
        self.all_fid.remove(fid)
        # 页码
        page = randint(3, 10)
        api = f'forum-{fid}-{page}.html'
        url = self.fullURL(api)
        html = self.request(url, post=False)

        if first_time:
            print('开始评论。\n每次评论需要间隔60秒。')
            # 第一次时，先获取一下现有金币数
            self.myMoney(False)

        soup = BeautifulSoup(html, 'html.parser')
        span = soup.find('a', href=f'forum-{fid}-1.html')
        if span and span.text:
            print(f'进入版块：{span.text}「{fid}」')

        # 提取板块下所有的帖子链接
        spans = soup.find_all('a', onclick='atarget(this)')
        # 板块内的贴子数(每个版块内最多回复3次)
        forum_reply_time = 0
        for span in spans:
            if not span.has_attr('style'):
                href = span['href']
                # 发表评论
                comment = choice(self.comments)
                # 从评论中随机取出一个进行发表
                if self.reply(comment, fid, href):
                    forum_reply_time += 1

                if forum_reply_time >= 3 or not self.config.canReply():
                    break

        # 评论数不够15条时，获取帖子下一页列表
        if self.config.canReply():
            self.forum_list()

    # 发表评论
    def reply(self, comment, fid, href):
        pattern = re.compile(r'\w*thread-(\d+)-\d+-\d+.\w+', re.S)
        items = re.findall(pattern, href)
        tid = items[0] if items else ''
        if not tid:
            print('帖子id不存在')
            return False

        url = self.fullURL(f'thread-{tid}-1-1.html')
        print(f'进入帖子：{url}')
        # 发表评论前的金币数
        money_history = self.my_money
        api_param = f'mod=post&action=reply&fid={fid}&tid={tid}&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
        url = self.encapsulateURL('forum.php', api_param)
        timestamp = int(time.time())
        c = quote(comment, 'utf-8')
        params = f'message={c}&posttime={timestamp}&formhash={self.formhash}&usesig=1&subject=++'
        # 非常感謝，回復發佈成功
        html = self.request(url, params)
        if html.find('非常感謝，回復發佈成功') > -1:
            self.config.reply_times += 1
            self.config.save()
            print(f'第{self.config.reply_times}条：「{comment}」-> 發佈成功')
            self.myMoney(False)
            if money_history == self.my_money:
                # 如果发表评论后，金币数不增加，就不再发表评论
                print('评论达到每日上限。不再发表评论。')
                self.config.reply_times = 99
                self.config.save()
            elif self.config.canReply():
                print(f'金钱：+{self.my_money - money_history}')
            # 评论有时间间隔限制
            print_sleep(60)
            return True
        elif html.find('抱歉，您所在的用戶組每小時限制發回帖') > -1:
            print('评论数超过限制')
            self.config.reply_times = 9999
            self.config.save()
            return True
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join([comment] + items) if items else html)
            # 评论有时间间隔限制
            if self.config.canReply():
                print_sleep(60)
            return False

    # 从空间链接中获取用户id
    def getUid(self, href):
        pattern = re.compile(r'\w*space-uid-(\d+).\w+', re.S)
        items = re.findall(pattern, href)
        return items[0] if items else ''

    # 访问别人空间
    def visitUserZone(self):

        if not self.config.is_visit_other_zone:
            return

        if self.user_href:
            url = self.user_href
            print(f'访问别人空间：{url}')
            self.request(url, post=False)
            self.config.is_visit_other_zone = False
            self.config.save()
            uid = self.getUid(url)
            if uid:
                self.leavMessage(uid)
        else:
            print('别人空间地址为空')

    # 留言
    def leavMessage(self, uid):
        if not self.config.is_leave_message:
            return

        if not uid:
            print('他人id为空')
            return

        self.myMoney()
        api_param = 'mod=spacecp&ac=comment&inajax=1'
        url = self.encapsulateURL('home.php', api_param)
        refer = quote(f'home.php?mod=space&uid={uid}', 'utf-8')
        message = quote('留个言，赚个金币。', 'utf-8')
        params = f'message={message}&refer={refer}&id={uid}&idtype=uid&commentsubmit=true&handlekey=commentwall_{uid}&formhash={self.formhash}'
        html = self.request(url, params)
        if html.find('操作成功') > -1:
            print('留言成功')
            self.config.is_leave_message = False
            self.config.save()
            pattern = re.compile(r'\{\s*\'cid\'\s*:\s*\'(\d+)\'\s*\}', re.S)
            items = re.findall(pattern, html)
            if items:
                cid = items[0]
                self.deleteMessage(cid)
            print_sleep(60)
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('留言失败')

    # 删除留言
    def deleteMessage(self, cid):
        if not cid:
            return
        # 获取删除留言相关参数
        self.headers['Referer'] = self.user_href
        api_param = f'mod=spacecp&ac=comment&op=delete&cid={cid}&handlekey=delcommenthk_{cid}&infloat=yes&handlekey=c_{cid}_delete&inajax=1&ajaxtarget=fwin_content_c_{cid}_delete'
        url = self.encapsulateURL('home.php', api_param)
        self.request(url, post=False)

        # 请求删除留言
        api_param = f'mod=spacecp&ac=comment&op=delete&cid={cid}&inajax=1'
        url = self.encapsulateURL('home.php', api_param)
        refer = quote(self.user_href, 'utf-8')
        params = f'referer={refer}&deletesubmit=true&formhash={self.formhash}&handlekey=c_{cid}_delete'
        html = self.request(url, params)
        if html.find('操作成功') > -1:
            print('删除留言成功')
            time.sleep(2)
            self.myMoney()
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('删除留言失败')

    # 获取我的金币数
    def myMoney(self, is_print=True):
        if not self.my_zone_url:
            return
        html = self.request(self.my_zone_url, post=False)
        pattern = re.compile(r'<li>金錢:\s*<a href=".*?">(\d+)</a>', re.S)
        items = re.findall(pattern, html)
        if items:
            money = int(items[0])
            self.my_money = money
            if is_print:
                print(f'金钱：{money}')
        else:
            print('获取金币失败')

    # 删除自己空间留言所产生的动态
    def delAllLeavMessageDynamic(self):
        if not self.my_uid:
            return

        print('获取留言动态')
        api_params = f'mod=space&uid={self.my_uid}&do=home&view=me&from=space'
        url = self.encapsulateURL('home.php', api_params)

        html = self.request(url, post=False)
        pattern = re.compile(r'"home.php\?mod=spacecp&amp;ac=feed&amp;op=menu&amp;feedid=(\d+)"')
        feedids = re.findall(pattern, html)
        if feedids:
            print(f'{len(feedids)}条动态')
        else:
            print('没有动态需要删除')
            return

        for feedid in feedids:
            self.delLeavMessageDynamic(feedid, url)

    # 删除一条动态
    def delLeavMessageDynamic(self, feedid, referer):
        if not feedid or not referer:
            return

        # 获取删除动态相关参数
        self.headers['Referer'] = referer
        api_param = f'mod=spacecp&ac=feed&op=menu&feedid={feedid}&infloat=yes&handlekey=a_feed_menu_{feedid}&inajax=1&ajaxtarget=fwin_content_a_feed_menu_{feedid}'
        url = self.encapsulateURL('home.php', api_param)
        self.request(url, post=False)

        api_params = f'mod=spacecp&ac=feed&op=delete&feedid={feedid}&handlekey=a_feed_menu_{feedid}&inajax=1'
        url = self.encapsulateURL('home.php', api_params)
        referer = quote(url, 'utf-8')
        params = f'referer={referer}&feedsubmit=true&formhash={self.formhash}'
        html = self.request(url, params)
        if html.find('操作成功') > -1:
            print('一条删除动态成功')
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('删除动态失败')

    # 发表一条记录
    def record(self):

        if not self.config.is_record:
            return

        if not self.my_uid:
            return

        refer = f'home.php?mod=space&uid={self.my_uid}&do=doing&view=me&from=space'
        api_param = 'mod=spacecp&ac=doing&view=me'
        url = self.encapsulateURL('home.php', api_param)
        header = {
            'Referer': self.fullURL(refer)
        }
        refer = quote(refer, 'utf-8')
        comment = choice(self.comments)
        message = quote(comment, 'utf-8')
        params = f'message={message}&add=&refer={refer}&topicid=&addsubmit=true&formhash={self.formhash}'
        html = self.request(url, params, header)
        if html.find(comment) > -1:
            print('发表记录成功')
            self.config.is_record = False
            self.config.save()
            id = self.findRecord(comment)
            self.delRecord(id, comment)
            print_sleep(90)
        else:
            print('发表记录失败')

    # 通过内容查找记录id
    def findRecord(self, comment, html=None):
        if not self.my_uid:
            return

        if not html:
            api_params = 'mod=space&do=doing&view=me'
            url = self.encapsulateURL('home.php', api_params)
            html = self.request(url, post=False)

        if html:
            html = html.replace('\n', '')
            pattern = re.compile(r'</a>:\s*<span>\s*(.*?)\s*</span>\s*</dd>\s*<dd\s+class\s*=\s*".*?"\s+id="(.*?)"\s+style\s*=\s*"display:none;"\s*>', re.S)
            recordids = re.findall(pattern, html)
            for id in recordids:
                if id and comment == id[0]:
                    return id[1]

    # 删除记录
    def delRecord(self, id, comment):
        if not id or id.find('_') < 0:
            return
        a = id.split('_')
        if not a or len(a) != 2:
            return
        start = a[0]
        end = a[1]

        api_params = f'mod=spacecp&ac=doing&op=delete&doid={end}&id=&handlekey=doinghk_{end}_&infloat=yes&handlekey={start}_doing_delete_{end}_&inajax=1&ajaxtarget=fwin_content_{start}_doing_delete_{end}_'
        url = self.encapsulateURL('home.php', api_params)
        self.request(url, post=False)

        referer = self.fullURL(f'home.php?mod=space&do=doing&view=me')
        api_params = f'mod=spacecp&ac=doing&op=delete&doid={end}&id=0'
        url = self.encapsulateURL('home.php', api_params)
        referer = quote(url, 'utf-8')
        params = f'handlekey={start}_doing_delete_{end}_&referer={referer}&deletesubmit=true&formhash={self.formhash}'
        html = self.request(url, params)
        print('删除记录成功' if not self.findRecord(comment, html) else f'删除记录失败:「{comment}」')

    # 发表日志
    def journal(self, money_history=None):

        if not self.config.canJournal():
            return

        self.login()
        # 发表前的金币数
        self.myMoney(False)
        money_history = self.my_money

        title = choice(self.comments)
        comments = []
        for _ in range(0, 10):
            comments.append(choice(self.comments))

        comment = '\n'.join(comments)
        api_params = 'mod=spacecp&ac=blog&blogid='
        url = self.encapsulateURL('home.php', api_params)
        header = {
            'Referer': self.fullURL(f'home.php?mod=space&uid={self.my_uid}&do=blog&view=me'),
            'Content-Type': f'multipart/form-data; boundary=----WebKitFormBoundary{random_all_string()}'
        }
        params = {
            'subject': title,
            'savealbumid': '0',
            'newalbum': '請輸入相冊名稱',
            'view_albumid': 'none',
            'message': comment,
            'formhash': self.formhash,
            'classid': '0',
            'tag': '',
            'friend': '0',
            'password': '',
            'selectgroup': '',
            'target_names': '',
            'blogsubmit': 'true'
        }
        html = self.request(url, params, header)
        print('发表日志成功' if html.find(title) > -1 else '发表日志失败')
        if html.find(title) > -1:
            self.config.journal_times += 1
            self.config.save()
            print(f'第{self.config.journal_times}篇日志：「{title}」-> 發佈成功')
            self.myMoney(False)
            if money_history == self.my_money:
                # 如果发表后，金币数不增加，就不再发表
                print('发表日志达到每日上限。')
                self.config.journal_times = 99
                self.config.save()
            else:
                print(f'金钱：+{self.my_money - money_history}')

            print_sleep(90)
        elif self.config.journal_faild_times < 3:
            self.config.journal_faild_times += 1
            print_sleep(90)
        else:
            print('发表日志失败')
            return

        # 发表有时间间隔限制
        if self.config.canJournal():
            self.journal()

    def delJournal(self, all_blogids=None):

        blogid = None
        # 先查出所有脚本发表的日志
        if all_blogids is None:
            all_blogids = []
            api_params = 'mod=space&do=blog&view=me'
            url = self.encapsulateURL('home.php', api_params)
            html = self.request(url, post=False)
            pattern = re.compile(r'<a\s+href\s*=\s*"blog-(\d+)-(\d+).html"\s+target\s*=\s*"_blank"\s*>\s*(.*?)\s*</a>', re.S)
            ids = re.findall(pattern, html)
            for id in ids:
                if id and id[0] == str(self.my_uid) and id[2] in self.comments:
                    all_blogids.append(id[1])
            if all_blogids:
                blogid = all_blogids[0] if not blogid else blogid
            else:
                print('没有需要删除的日志')
                return

        if not blogid:
            return

        api_params = f'mod=spacecp&ac=blog&op=delete&blogid={blogid}'
        url = self.encapsulateURL('home.php', api_params)
        referer = self.fullURL('home.php?mod=space&do=blog&view=me')
        params = {
            'referer': quote(referer, 'utf-8'),
            'deletesubmit': 'true',
            'formhash': self.formhash,
            'btnsubmit': 'true'
        }
        self.request(url, self.paramsString(params))
        if all_blogids:
            all_blogids.remove(blogid)

        if all_blogids:
            print_sleep(15)
            self.delJournal(all_blogids)

    # 发布一个分享
    def share(self):

        if not self.config.canShare():
            return

        self.login()
        # 发表前的金币数
        self.myMoney(False)
        money_history = self.my_money

        api_params = f'mod=space&uid={self.my_uid}&do=share&view=me&quickforward=1'
        url = self.encapsulateURL('home.php', api_params)
        self.request(url, post=False)
        print_sleep(2)

        api_params = 'mod=spacecp&ac=share&type=link&view=me&from=&inajax=1'
        url = self.encapsulateURL('home.php', api_params)
        referer = f'home.php?mod=space&uid={self.my_uid}&do=share&view=me&quickforward=1'
        params = {
            'link': quote('http://www.baidu.com', 'utf-8'),
            'general': quote('123123123', 'utf-8'),
            'referer': quote(referer, 'utf-8'),
            'sharesubmit': 'true',
            'formhash': self.formhash,
            'handlekey': 'shareadd'
        }
        header = {
            'Referer': self.fullURL(referer)
        }
        html = self.request(url, self.paramsString(params), header)
        if html.find('操作成功') > -1:
            print('发布分享成功')
            self.config.share_times += 1
            self.config.save()
            print_sleep(10)
            self.myMoney(False)
            if money_history == self.my_money:
                # 如果发表后，金币数不增加，就不再发表
                print('发表分享达到每日上限。')
                self.config.share_times = 99
                self.config.save()
            else:
                print(f'金钱：+{self.my_money - money_history}')

            # 删除刚发表的分享
            pattern = re.compile(r'\{\s*\'sid\'\s*:\s*\'(\d+)\'\s*\}', re.S)
            items = re.findall(pattern, html)
            if items:
                sid = items[0]
                self.delShare(sid)
            print_sleep(50)
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('发布分享失败')
            if self.config.share_faild_times < 3:
                self.config.share_faild_times += 1
            else:
                return

        if self.config.canShare():
            self.share()

    # 删除一条分享
    def delShare(self, sid):
        if not sid:
            return

        api_params = f'mod=spacecp&ac=share&op=delete&sid={sid}&type=&inajax=1'
        url = self.encapsulateURL('home.php', api_params)
        params = {
            'referer': quote(self.fullURL('home.php?mod=space&do=share&view=me'), 'utf-8'),
            'deletesubmit': 'true',
            'formhash': self.formhash,
            'handlekey': f's_{sid}_delete'
        }
        html = self.request(url, self.paramsString(params))
        if html.find('操作成功') > -1:
            print('删除分享成功')
        else:
            pattern = re.compile(r'\[CDATA\[(.*?)<', re.S)
            items = re.findall(pattern, html)
            print('\n'.join(items) if items else html)
            print('删除分享失败')

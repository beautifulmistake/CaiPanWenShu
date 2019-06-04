"""
此爬虫先使用 requests 实现,从中学习一下别人编写的思路以及对某些关键点上的处理方式,总结出一些适用于自己的方法
# # 创建一个cookie对象
# c = requests.cookies.RequestsCookieJar()
# 更新cookies
# c.set('vjkl5', res.cookies["vjkl5"])
# session.cookies.update(c)
"""
import random
from urllib import parse

import execjs
import requests


# 创建 session 对象
session = requests.Session()

# 打开并读取 v15x.js 文件
with open(r'F:\CaiPanWenShu\CaiPanWenShu\prepare\v15x.js', 'r', encoding='utf-8') as f:
    js = f.read()
    ctx = execjs.compile(js)
# 此处暂时省略了二层加密方法


def get_guid():
    """
    获取 guid 参数
    :return:
    """
    # 原js版本
    # js1 = '''
    #   function getGuid() {
    #         var guid = createGuid() + createGuid() + "-" + createGuid() + "-" + createGuid() + createGuid() + "-" +
    #         createGuid() + createGuid() + createGuid(); //CreateGuid();
    #           return guid;
    #     }
    #     var createGuid = function () {
    #         return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
    #     }
    #     '''
    # ctx1 = execjs.compile(js1)
    # guid = (ctx1.call("getGuid"))
    # return guid
    # python 实现版本
    def createGuid():
        return str(hex((int(((1 + random.random()) * 0x10000)) | 0)))[3:]
    return '{}{}-{}{}-{}{}'.format(createGuid(), createGuid(), createGuid(), createGuid(), createGuid(), createGuid())


def get_number(guid):
    """
    获取 number 参数
    :param guid:
    :return:
    """
    codeUrl = "http://wenshu.court.gov.cn/ValiCode/GetCode"
    data = {
        'guid': guid
    }
    headers = {
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'Referer': 'http://wenshu.court.gov.cn/',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
    }
    res = session.post(codeUrl, data=data, headers=headers)
    return res.text


def get_vjkl5(guid, number, param):
    """
    获取cookies 中 设置的 vjk15
    :param guid: guid
    :param number: number
    :param param: 高级检索的条件
    :return: vjk15
    """
    # 请求的URL
    url = "http://wenshu.court.gov.cn/list/list/?sorttype=1&" \
          "number={number}&guid={guid}&conditions=searchWord+QWJS++{param}"
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'Host': 'wenshu.court.gov.cn',
        # 'Cookie': '_gscu_2116842793=57716337d6mv2i41; wzws_cid=14ff05c4ba44bed9cdf4f7060ff37168417e47b1eb6146499cfc098a878affe758b0155b1e4ddb18b9455dd2e23be7129b1311352120c4677892b4870b42c7a6'
    }
    url_ = url.format(number=number, guid=guid, param=param)
    print(url_)
    res = session.get(url=url_, headers=headers, timeout=10)
    try:
        vjkl5 = res.cookies["vjkl5"]
        return vjkl5
    except:
        # 请求失败,重新发起
        # get_vjkl5(guid, number, param)
        print("请求失败")


def get_vl5x(vjkl5):
    """
    根据 vjk15 获取 v15x 参数
    :param vjkl5:
    :return:
    """
    vl5x = (ctx.call('GetVl5x', vjkl5))
    return vl5x


def construct_param():
    """
    构造检索条件
    :return:
    """
    # 通用模板 conditions=searchWord+1+AJLX++案件类型:刑事案件
    template = "conditions=searchWord++{0}++{1}:{2}"
    # 检索关键字
    keyword = input("请输入需要搜索的内容: \n").strip()
    # 检索类型
    search_type_list = ["全文检索", "首部", "事实", "理由", "判决结果", "尾部"]
    user_search_type = input("请输入你想要检索的类型:[全文检索, 首部, 事实, 理由, 判决结果, 尾部] \n")
    search_type = user_search_type.strip() if user_search_type else search_type_list[0]   # 如果用户没有设置,采用此值
    # 案由
    case_list = ['请选择', '刑事案由', '民事案由', '行政案由', '赔偿案由']
    user_case = input("请输入你想要检索的案由:[请选择, 刑事案由, 民事案由, 行政案由, 赔偿案由]\n")
    case = user_case.strip() if user_case else case_list[0]
    # 法院层级
    court_type_list = ['全部', '最高法院', '高级法院', '中级法院', '基层法院']
    user_court_type = input("请输入你要检索的法院层级:[全部, 最高法院, 高级法院, 中级法院, 基层法院]\n")
    court_type = user_court_type.strip() if user_court_type else court_type_list[0]
    # 案件类型
    case_type_list = ['请选择', '刑事案件', '民事案件', '行政案件', '赔偿案件', '执行案件']
    user_case_type = input("请输入你要检索的案件类型:[请选择, 刑事案件, 民事案件, 行政案件, 赔偿案件, 执行案件]\n")
    case_type = user_case_type.strip() if user_case_type else case_type_list[0]
    # 审判程序
    case_process_list = ['请选择', '一审', '二审', '再审', '再审审查与审判监督', '其他']
    user_case_process = input("请输入你要检索的审判程序:[请选择, 一审, 二审, 再审, 再审审查与审判监督, 其他]\n")
    case_process = user_case_process.strip() if user_case_process else case_process_list[0]
    # 文书类型
    wenshu_type_list = ['全部', '判决书', '裁定书', '调解书', '决定书', '通知书', '批复', '答复', '函', '令', '其他']
    user_wenshu_type = input("请输入你要检索的文书类型:[全部, 判决书, 裁定书, 调解书, 决定书, 通知书, 批复, 答复, 函, 令, 其他]\n")
    wenshu_type = user_wenshu_type.strip() if user_wenshu_type else wenshu_type_list[0]
    # 裁判日期
    start_date = input("请输入你要检索的起始日期[year-month-day]:\n")
    end_date = input("请输入你要检索的截至日期[year-month-day]:\n")
    # 创建存储高级检索条件的列表
    param_list = list()
    # 添加检索类型和关键字,最常用的方法
    param_list.append(template.format(keyword, search_type, keyword))
    # 添加案由检索条件
    if case != "请选择":
        param_list.append(template.format("AY", "案由", case))
    # 添加法院层级检索条件
    if court_type != "全部":
        param_list.append(template.format("FYCJ", "法院层级", court_type))
    # 添加案件类型检索条件
    if case_type != "请选择":
        param_list.append(template.format("AJLX", "案件类型", case_type))
    # 添加审判程序检索条件
    if case_process != "请选择":
        param_list.append(template.format("SPCX", "审判程序", case_process))
    # 添加文书类型检索条件
    if wenshu_type != "全部":
        param_list.append(template.format("WSLX", "文书类型", wenshu_type))
    # 添加裁判日期
    if start_date and end_date:
        param_list.append("conditions=searchWord++CPRQ++裁判日期:{}%20TO%20{}".format(start_date.strip(), end_date.strip()))
    # 根据以上检索的条件构造 conditions
    param = '&'.join(param_list)
    return param


def get_list_page(Param, Page=10, Order='法院层级', Direction='asc'):
    """
    根据检索条件发起请求,获取列表页的数据
    :param Param: 检索条件
    :param Page: 每页显示的条数 固定为10条
    :param Order: 默认采用按 法院层级 排序规则
    :param Direction: 默认采用 按照日期的升序排序方式, 可选参数
    :return:
    """
    # 获取guid
    guid = get_guid()
    print("查看guid:", guid)
    # 获取 number
    number = get_number(guid)
    print(number)
    # 获取 vjk15
    vjkl5 = get_vjkl5(guid, number, Param)
    print(vjkl5)
    # 获取 v15x
    vl5x = get_vl5x(vjkl5)
    print(vl5x)
    # 请求URL
    url = "http://wenshu.court.gov.cn/List/ListContent"
    # 请求头
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        "Param": Param,
        "Index": 1,
        "Page": Page,
        "Order": Order,
        "Direction": Direction,
        "vl5x": vl5x,
        "number": number,
        "guid": guid
    }
    # 发起请求
    res = session.post(url=url, headers=headers, data=data)
    print("查看cookies:", session.cookies.get_dict())
    if res.status_code == 200:
        res.encoding = res.apparent_encoding
        print("查看响应:", res.text)


def test_cookie():
    """
    此方法用于验证请求 get_vjkl5 函数,特别注意此时 cookie 有时效性
    :return:
    """
    # 获取 guid
    guid = get_guid()
    print("查看guid:", guid)
    # 获取 number
    number = get_number(guid)
    print("查看 number:", number)
    # 请求的URL
    url = "http://wenshu.court.gov.cn/list/list/?sorttype=1&number={number}&" \
          "guid={guid}&conditions=searchWord+{keyword}+QWJS++{type}:{keyword}".\
        format(number=number, guid=guid, keyword=parse.quote("知识产权"), type=parse.quote("全文检索"))
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'Host': 'wenshu.court.gov.cn',
        'Cookie': '_gscu_2116842793=57716337d6mv2i41; _gscbrs_2116842793=1; '
                  'Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2=1557716337,1557793068,1557900479; '
                  'vjkl5=cf874a995ff2ebee20177188f3ce886fe988cf7c; _gscs_2116842793=t5796770'
                  '1y2xy7c20|pv:4; Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2=1557968887; '
                  'wzws_cid=0e9961b81fa6a292800e3b919415e0b9d871680c5f2604fcb6021e27ab49'
                  'a051bd45c9e365ec701db6ec5372b239b53b07afdbef55e613c5fc234f5d7b01d75f'
    }
    print(url)
    res = session.get(url=url, headers=headers)
    res.encoding = res.apparent_encoding
    print(res.text)
    vjkl5 = res.cookies["vjkl5"]
    print(vjkl5)
    return vjkl5


def test_list_page():
    """
    此方法用于测试获取列表页响应需要哪些参数
    以下参数是进过测试需要携带的参数,其中 Referer 不是必须的,cookie是必须的参数,测试时似乎也不像之前一样 cookie 有时效性
    其中在测试阶段共有三种类型的响应:
    1.正确的响应(响应的是一个字符串结果)
    2.响应的内容提示需要加载 JavaScript 脚本(由于没有携带cookie的缘故)
    3.响应内容的 remind key (这是一个需要输入验证码的页面)
    :return:
    """
    # 请求URL
    url = "http://wenshu.court.gov.cn/List/ListContent"
    # 请求头
    headers = {
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'wenshu.court.gov.cn',
        'Origin': 'http://wenshu.court.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': '_gscu_2116842793=57716337d6mv2i41; wzws_cid=cc0b7795a7bbe9b0799cf88fbb5dc4ada94cba9d7530900a95fbe0fd1c1155ff741c2d0614d029e86aef29489f3e310430eea021a594d9b9371ea30929e31459; Hm_lvt_d2caefee2de09b8a6ea438d74fd98db2=1557974208; _gscbrs_2116842793=1; vjkl5=dc6c095ff81be1c0194180e49c1258e6ce47a350; _gscs_2116842793=57974208pcbs5q97|pv:2; Hm_lpvt_d2caefee2de09b8a6ea438d74fd98db2=1557974327',
    }
    # 请求参数
    data = {
        "Param": '全文检索:知识产权',
        "Index": 1,
        "Page": 10,
        "Order": '法院层级',
        "Direction": 'asc',
        "vl5x": 'a28ed3293ad67736d1647283',
        "number": 'Q5MU',
        "guid": '532c231f-5a3f-587cd00b-9ad838d1aa7d'
    }
    # 发起请求
    res = session.post(url=url, headers=headers, data=data)
    if res.status_code == 200:
        res.encoding = res.apparent_encoding
        print("查看响应:", res.text)


def login():
    """
    所有的cookie 都有有效期
    :return:
    """
    url = "http://wenshu.court.gov.cn/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'Host': 'wenshu.court.gov.cn',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cookie': '_gscu_2116842793=57716337d6mv2i41; '
                  'wzws_cid=53d63358b50a99d917b397d7511e62d1d7e408ced42a80796dc077'
                  '79229b7cb1d74fb1e7dd099f323cd9009877df79cb05931d2e07988eb9cbc6185e2a5deb84'
    }
    # 发起请求
    res = session.get(url=url, headers=headers)
    if res.status_code == 200:
        res.encoding = res.apparent_encoding
        print("查看响应:", res.text)


# 测试代码
if __name__ == "__main__":
    # 测试整体的代码
    # login()
    # param = construct_param()
    # print(param)
    # get_list_page(param)
    # 测试 get_vjkl5 方法
    # test_cookie()
    # 测试 get_list_page 方法
    # test_list_page()
    # 测试首页函数
    login()

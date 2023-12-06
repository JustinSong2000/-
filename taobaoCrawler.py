import hashlib
import json
import random
import sys
import time
from urllib.parse import urlparse, parse_qs

import pandas
import pandas as pd
import requests
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import LogUtil
from searchItem import SearchItem, ResultItem

# 日志设置
logger = LogUtil.init_log()


def login_all():
    if "needlogin" in sys.argv:
        logger.info("需要登录")
        login("taobao")
        login("tianmao")


def handel_input_csv():
    result = []
    df = pd.read_csv('/Users/justin_song/Desktop/crawl.csv', encoding='utf-8')
    for index, row in df.iterrows():
        keyword = row['关键词']
        version = row['版本']
        region = row['适用地区']
        subject = row['科目']
        min_price = row['最低价格']
        start_page = row['起始页']
        end_page = row['结束页']
        if '，' not in min_price:
            item = SearchItem(keyword, version, region, [], [min_price], start_page, end_page)
        else:
            item = SearchItem(keyword, version, region, subject.split("，"), min_price.split("，"), start_page, end_page)
        result.append(item)
    return result


def convert_cookie_to_dict(input_string):
    result_dict = {}
    input_string += ";"
    pairs = input_string.split(';')
    for pair in pairs:
        if pair != '':
            key, value = pair.split('=', 1)
            result_dict[key.strip()] = value.strip()
    return result_dict


def addCookie(driver, type):
    if type == "taobao":
        with open('taobao_cookies.txt', 'r', encoding='utf8') as f:
            listCookies = json.loads(f.read())
    if type == "tianmao":
        with open('tm_cookies.txt', 'r', encoding='utf8') as f:
            listCookies = json.loads(f.read())
    for cookie in listCookies:
        expires = ''
        # domain = ''
        if cookie.get('expiry') is not None:
            expires = cookie.get('expiry')
        # if cookie.get('domain') is not None:
        #     expires = cookie.get('domain')
        cookie_dict = {
            'domain': cookie.get('domain'),
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            'path': cookie.get('path'),
            'httpOnly': cookie.get('httpOnly'),
            'HostOnly': cookie.get('hostOnly'),
            'Secure': cookie.get('secure'),
            'Expires': expires,
            'SameSite': cookie.get('sameSite'),
        }
        driver.add_cookie(cookie_dict)
        # browser_detail.add_cookie(cookie_dict)
    time.sleep(2)
    driver.refresh()
    # browser_detail.refresh()


def swipe_down(driver):
    second = random.randint(2, 5)
    for i in range(int(second / 0.1)):
        js = "var q=document.documentElement.scrollTop=" + str(100 * i)
        driver.execute_script(js)
        time.sleep(0.1)
    js = "var q=document.documentElement.scrollTop=100"
    driver.execute_script(js)


def swipe_up(driver):
    second = random.randint(2, 5)
    for i in range(int(second / 0.1)):
        js = "var q=document.documentElement.scrollTop=" + str(1000 - 100 * i)
        driver.execute_script(js)
        time.sleep(0.1)
    js = "var q=document.documentElement.scrollTop=0"
    driver.execute_script(js)


def get_sign(data, cookies, t, app_key):
    datas = f'{cookies["_m_h5_tk"].split("_")[0]}&{str(t)}&{app_key}&{data}'
    sign = hashlib.md5()  # 创建md5对象
    sign.update(datas.encode(encoding='utf-8'))  # 使用md5加密要先编码，不然会报错，我这默认编码是utf-8
    signs = sign.hexdigest()  # 加密
    return signs


def get_detail_by_url(itemLink):
    try:
        parsed_url = urlparse(itemLink)
        query_params = parse_qs(parsed_url.query)
        id = query_params['id'][0]
        t = int(time.time() * 1000)
        # abbucket = query_params['abbucket'][0]
        # ns = query_params['ns'][0]
        # sku_properties = query_params['sku_properties'][0]
        exParams = {
            "ali_refid": "a3_430585_1006:1121054187:N:csp1May7p6LZGxaXUuM7DQ==:f3105df18d4c8dcecb71902beb9c11c8",
            "ali_trackid": "162_f3105df18d4c8dcecb71902beb9c11c8",
            "id": id,
            "queryParams": f"ali_refid=a3_430585_1006%3A1121054187%3AN%3Acsp1May7p6LZGxaXUuM7DQ%3D%3D%3Af3105df18d4c8dcecb71902beb9c11c8&ali_trackid=162_f3105df18d4c8dcecb71902beb9c11c8&id={id}",
            'domain': "https://detail.tmall.com",
            'path_name': "item.htm"
        }
        data = {
            'id': id,
            'detail_v': '3.3.2',
            'exParams': json.dumps(exParams),
        }
        params = {
            'jsv': '2.6.1',
            't': t,
            'appkey': "12574478",
            'api': 'mtop.taobao.pcdetail.data.get',
            'v': '1.0',
            'isSec': 0,
            'ecode': 0,
            'timeout': 10000,
            'ttid': '2022@taobao_litepc_9.17.0',
            'AntiFlood': 'true',
            'AntiCreep': 'true',
            'preventFallback': 'true',
            'type': 'jsonp',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp1',
            'data': json.dumps(data)
        }
        dictCookies = browser.get_cookies()
        jsonCookies = json.dumps(dictCookies)
        listCookies = json.loads(jsonCookies)
        detail_tm_cookie = {}
        for cookie in listCookies:
            detail_tm_cookie[cookie.get('name')] = cookie.get('value')
        headers = {
            'authority': 'h5api.m.tmall.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://detail.tmall.com/',
            'sec-ch-ua': 'Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'script',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-site',
            'user-agent': UserAgent().random,  # 随机生成一个User-Agent
            'sign': get_sign(data=data, cookies=detail_tm_cookie, t=t, app_key="12574478")
        }
        response = requests.get(url="https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/", params=params,
                                cookies=detail_tm_cookie, headers=headers)
        print(response)
        print("获取商品信息遇到错误")
    except Exception:
        pass


# copy browser1 -> browser2
def copyCookies(browser1, browser2):
    browser2.delete_all_cookies()
    dictCookies = browser1.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    listCookies = json.loads(jsonCookies)
    for cookie in listCookies:
        expires = ''
        if cookie.get('expiry') is not None:
            expires = cookie.get('expiry')
        cookie_dict = {
            'domain': cookie.get('domain'),
            'name': cookie.get('name'),
            'value': cookie.get('value'),
            'path': cookie.get('path'),
            'httpOnly': cookie.get('httpOnly'),
            'HostOnly': cookie.get('hostOnly'),
            'Secure': cookie.get('secure'),
            'Expires': expires,
            'SameSite': cookie.get('sameSite'),
        }
        browser2.add_cookie(cookie_dict)
    browser2.refresh()


def getCookie():
    dictCookies = browser.get_cookies()  # 获取list的cookies
    jsonCookies = json.dumps(dictCookies)  # 转换成字符串保存
    with open('taobao_cookies.txt', 'w') as f:
        f.write(jsonCookies)
    logger.info('cookies保存成功！')


def getTMCookie():
    dictCookies = browser_detail.get_cookies()  # 获取list的cookies
    jsonCookies = json.dumps(dictCookies)  # 转换成字符串保存
    with open('tm_cookies.txt', 'w') as f:
        f.write(jsonCookies)
    logger.info('tiammao === cookies保存成功！')


def login(type):
    if type == "taobao":
        browser.get('https://login.taobao.com/member/login.jhtml')
        logger.info("请登录")
        # 循环检测是否成功登录
        while browser.title != '我的淘宝':
            logger.warning('请确保已经登录淘宝并在【我的淘宝】页面')
            time.sleep(5)
        getCookie()
    if type == "tianmao":
        browser_detail.get(
            "https://login.taobao.com/?redirectURL=https%3A%2F%2Fwww.tmall.com%2F%3Fspm%3Da2233.7711963.a2226mz.1.1dcf7fb81oLyZN")
        while 'www.tmall.com/?spm' not in browser_detail.current_url:
            logger.warning('请确保已经登录天猫')
            time.sleep(5)
        getTMCookie()


# type common 表示商品list页面弹窗
#  detail 表示商品详情页面弹窗
def detectSlider(web_driver, type):
    try:
        trys = 0
        while trys < 500000:
            time.sleep(2)
            trys += 1
            logger.debug(f"尝试{trys}次滑块 === {type}")
            if type == 'common':
                web_driver.switch_to.frame(1)
            # print(browser.page_source)
            if type == 'detail':
                web_driver.switch_to.frame(0)
            slider = web_driver.find_element(By.ID, 'nc_1_n1z')
            ActionChains(web_driver).click_and_hold(slider).perform()
            trace = [31, 29, 41, 39, 25, 35, 33, 37]
            random.shuffle(trace)
            logger.info(trace)
            for i in range(len(trace)):
                yoffset_random = random.uniform(-2, 4)
                duration = random.randint(20, 70)
                ActionChains(web_driver, duration=duration).move_by_offset(xoffset=trace[i],
                                                                           yoffset=yoffset_random).perform()
                # print(f"第{trys}次的off---x:{slider.location.get('x')}")
            ActionChains(web_driver).release().perform()
            # print(browser.page_source)
            web_driver.refresh()

    except Exception:
        logger.info(f"{type} === 没找到滑块验证")


def get_detail(itemLink, sku_grade, sku_subject, sku_price):
    # copyCookies(browser, browser_detail)
    browser_detail.get(itemLink)
    random_swip_down(browser_detail)
    detectSlider(browser_detail, type="detail")
    time.sleep(2)
    skuCateElem = []
    result_items = []
    skuCateElem = browser_detail.find_element(By.CLASS_NAME, 'BasicContent--sku--6N_nw6c').find_elements(By.CLASS_NAME,
                                                                                                         'skuCate')
    for elem in skuCateElem:
        skuName = split_sku_name(elem.text)
        skuElements = elem.find_elements(By.CLASS_NAME, 'skuItem ')
        if skuName == "版本":
            for sku_inner_element in skuElements:
                time.sleep(0.5)
                sku_inner_element.click()
        if "学龄" in skuName or "适用地区" in skuName:
            for sku_inner_element in skuElements:
                time.sleep(0.5)
                if sku_grade in sku_inner_element.text:
                    sku_inner_element.click()
        if skuName == "科目":
            for sku_inner_element in skuElements:
                time.sleep(0.5)
                ind = check_match(sku_inner_element.text, sku_subject)
                if ind != -1:
                    sku_inner_element.click()
                    price_it = browser_detail.find_element(By.CLASS_NAME, 'Price--normal--t-x499v').text
                    real_price = split_price(price_it)
                    if float(real_price) < float(sku_price[ind]):
                        ite = ResultItem(sku_inner_element.text, real_price, sku_price[ind])
                        result_items.append(ite)
        if not sku_subject:
            price_it = browser_detail.find_element(By.CLASS_NAME, 'Price--normal--t-x499v').text
            real_price = split_price(price_it)
            if float(real_price) < float(sku_price[0]):
                ite = ResultItem("default", real_price, sku_price[0])
                result_items.append(ite)
        time.sleep(0.5)
    return result_items


def split_sku_name(original_string):
    result = original_string.split("：\n")[0]
    return result


def split_price(input_string):
    if "折后" in input_string or "券后" in input_string:
        return input_string.split("¥")[2]
    else:
        return input_string.split("¥")[1]


def check_match(str, strArray):
    if str in strArray:
        return strArray.index(str)
    else:
        for s in strArray:
            if s in str:
                return strArray.index(s)
        return -1


def random_swip_down(driver):
    i = random.randint(0, 3)
    time.sleep(i)


prefs = {
    'profile.default_content_setting_values': {
        'notifications': 2
    },
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
}
# 淘宝页面版本 0旧 1新
tbPageVersion = 1
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
options.add_argument("user-agent=" + UserAgent().random)
# options.add_argument('--headless')
options.add_argument('--disable-blink-features')
options.add_argument('--disable-blink-features=AutomationControlled')  # 去除浏览器selenium监控
options.add_argument('--disable-gpu')  # 禁用GPU加速
options.add_argument("--disable-popup-blocking")  # 关闭弹窗拦截，不然新页面打不开
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--no-sandbox')  # 以最高权限运行
options.add_experimental_option('prefs', prefs)
options.add_argument('disable-infobars')  # 隐藏"Chrome正在受到自动软件的控制"
browser = webdriver.Chrome(options=options)
browser_detail = webdriver.Chrome(options=options)
with open("stealth.min.js") as f:
    js = f.read()
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": js})
browser_detail.maximize_window()
browser.maximize_window()
login_all()
browser.get(f'https://s.taobao.com/search?q={"鞋子"}')
addCookie(driver=browser, type="taobao")
browser_detail.get(f'https://www.tmall.com/?spm=a21bo.jianhua.201859.1.5af92a89D9jzEs')
addCookie(driver=browser_detail, type="tianmao")
swipe_down(browser_detail)
time.sleep(2)
logger.info("开始处理弹窗")
#############
browser.get(f'https://s.taobao.com/search?q={"鞋子"}')
detectSlider(browser, "common")
time.sleep(2)
# 输出列表准备
output_list = []
logger.info("登录成功")
# 循环爬取程序
searchItems = handel_input_csv()
for item in searchItems:
    keyword = item.keyword
    region = item.region
    subject = item.subject
    min_price = item.min_price
    is_all_down = False
    start_p = item.start_page
    end_p = item.end_page
    browser.get(f'https://s.taobao.com/search?q={keyword}')
    for page in range(start_p, end_p):
        try:
            logger.info(f'当前正在获取第{page}页，还有{end_p - start_p - page}页')
            if is_all_down:
                break
            if page != start_p:
                next_page_button = browser.find_element(By.CSS_SELECTOR,
                                                        '#sortBarWrap > div.SortBar--sortBarWrapTop--VgqKGi6 > div.SortBar--otherSelector--AGGxGw3 > div:nth-child(2) > div.next-pagination.next-small.next-simple.next-no-border > div > button.next-btn.next-small.next-btn-normal.next-pagination-item.next-next')
                next_page_button.click()
            # 按价格升序排序
            if page == 1:
                ActionChains(browser, duration=50).move_to_element(
                    browser.find_element(By.CLASS_NAME, "next-tabs-nav-scroll").find_elements(By.CLASS_NAME,
                                                                                              "next-tabs-tab-inner")[
                        3]).perform()
                ActionChains(browser, duration=100).pause(2).move_to_element(
                    browser.find_elements(By.CLASS_NAME, "SortBar--priceTag--hXumFre")[0]).click().perform()
            swipe_down(browser)
            swipe_up(browser)
            logger.info('using new version selector')
            time.sleep(2)
            goods_arr = browser.find_elements(By.CSS_SELECTOR,
                                              '#root > div > div:nth-child(2) > div.PageContent--contentWrap--mep7AEm > div.LeftLay--leftWrap--xBQipVc > div.LeftLay--leftContent--AMmPNfB > div.Content--content--sgSCZ12 > div>div')
            goods_length = len(goods_arr)
            for i, goods in enumerate(goods_arr):
                try:
                    i = i + 1
                    if i == 1:
                        # 检查第一个商品的价格
                        item_price_int = goods.find_element(By.CSS_SELECTOR,
                                                            f'div:nth-child({i})>a>div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--priceInt--ZlsSi_M').text
                        item_price_float = goods.find_element(By.CSS_SELECTOR,
                                                              f'div:nth-child({i})>a>div> div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--priceFloat--h2RR0RK').text
                        item_price = item_price_int + item_price_float
                        if float(item_price) >= float(item.all_sku_min_price):
                            is_all_down = True
                            break
                    logger.info(f'正在获取第{i}个,共计{goods_length}个')
                    item_name = goods.find_element(By.CSS_SELECTOR,
                                                   f'div:nth-child({i})>a>div > div.Card--mainPicAndDesc--wvcDXaK > div.Title--descWrapper--HqxzYq0 > div > span').text
                    if keyword not in item_name:
                        time.sleep(2)
                        continue
                    item_shop = goods.find_element(By.CSS_SELECTOR,
                                                   f'div:nth-child({i})>a>div> div.ShopInfo--shopInfo--ORFs6rK  > div>a').text
                    month_deals = goods.find_element(By.CSS_SELECTOR,
                                                     f'div:nth-child({i}) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--realSales--FhTZc7U').text.replace(
                        '人付款', '').replace('人收货', '')
                    if month_deals == '0人收货':
                        time.sleep(1)
                        continue
                    ships_from_province = goods.find_element(By.CSS_SELECTOR,
                                                             f'div:nth-child({i}) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > div:nth-child(5) > span').text
                    ships_from_city = ''
                    shop_link = goods.find_element(By.CSS_SELECTOR,
                                                   f'div:nth-child({i})>a>div> div.ShopInfo--shopInfo--ORFs6rK  > div>a').get_attribute(
                        'href')
                    item_link = goods.find_element(By.CSS_SELECTOR, f'div:nth-child({i})>a').get_attribute('href')
                    # 表示进入淘宝老页面
                    # 就不进入细节查看了
                    if "taobao" in item_link:
                        time.sleep(1)
                        continue
                    # 在这里进入商品详情
                    time.sleep(1)
                    result_items = []
                    try:
                        result_items = get_detail(itemLink=item_link, sku_subject=subject, sku_price=min_price,
                                                  sku_grade=region)
                    except Exception:
                        try:
                            element = browser_detail.find_element(By.CLASS_NAME, "baxia-punish")
                            logger.error("监测到滑块困难验证码，尝试绕过")
                            login("tianmao")
                            # browser_detail.delete_all_cookies()
                            browser_detail.get(item_link)
                            # addCookie(browser_detail, "tianmao")
                            detectSlider(browser_detail, "tianmao")
                            while True:
                                try:
                                    punish_element = browser_detail.find_element(By.CLASS_NAME,
                                                                                 "J_MIDDLEWARE_FRAME_WIDGET")
                                    logger.warning("等待滑块验证通过")
                                    time.sleep(1)
                                except Exception:
                                    logger.info("滑块验证成功")
                                    result_items = get_detail(itemLink=item_link, sku_subject=subject,
                                                              sku_price=min_price,
                                                              sku_grade=region)
                                    break
                        except Exception:
                            logger.error("滑块验证遇到未知问题")
                    if result_items is []:
                        time.sleep(1)
                        logger.warning(f"{keyword}======未找到任何商品")
                        continue
                    for result_item in result_items:
                        goods_item = {"商品名称": item_name, "命中关键词": keyword, "sku学科": result_item.subject,
                                      "商品价格": result_item.price, "设定最低价": result_item.sku_price,
                                      "差价": result_item.diffs,
                                      "月销售量": month_deals, "商品店铺名称": item_shop,
                                      "归属地": ships_from_province + ' ' + ships_from_city,
                                      "商品链接": item_link, }
                        output_list += [goods_item]
                    time.sleep(1)
                except Exception:
                    logger.error(f"当前{page}出现问题, 本页扫描完成{i}/{goods_length}")
                    continue
        except Exception:
            logger.error(f'查询==={item.keyword}===遇到错误====')
            continue

logger.info('正在导出xlsx')
output_dataframe = pandas.DataFrame(output_list)
output_dataframe.to_excel('淘宝爬取商品结果' + f'{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}' + '.xlsx',
                          index=False)
logger.info('保存文件完成，准备退出中')
time.sleep(5)
browser.close()
browser.quit()
sys.exit()

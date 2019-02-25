import time
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

# 设置回帖量下限值
M = 3000
# get请求模版进入贴吧  第一个花括号为贴吧名，第二个的页码
template_url = "https://tieba.baidu.com/f?kw={name}&ie=utf-8&pn={sum}"
template_url1 = "https://tieba.baidu.com/f?kw={name}"
def extra_from_one_page(page_lst):
    '''从一页中提取 帖子'''
    # 临时列表保存字典数据，每一个帖子都是一个字典数据
    tmp = []
    for i in page_lst:
        # 判断是否超过阈值
        if int(i.find(class_='threadlist_rep_num').text) > M:
            dic = {}
            # 点击量
            dic['num'] = int(i.find(class_='threadlist_rep_num').text)
            # 帖子名称
            dic['name'] = i.find(class_='threadlist_title').text
            # 帖子地址
            dic['address'] = 'https://tieba.baidu.com' + i.find(class_='threadlist_title').a['href']

            tmp.append(dic)
    return tmp

def get_page_lst(target_url):
    while 1:
        i = 1
        print("第"+str(i)+"次请求："+target_url)
        try:
            res = requests.get(target_url)

            # 转为 bs 对象
            soup = BeautifulSoup(res.text, 'html.parser')

            # 获取该页帖子列表
            page_lst = soup.find_all(class_='j_thread_list')
            return page_lst
        except:
                print("请求异常等待10秒再请求")
                time.sleep(10000)
                i += 1;


def get_num(name):
    target_url = template_url1.format(name=name)

    res =requests.get(target_url)

    # 转为 bs 对象
    soup = BeautifulSoup(res.text, 'html.parser')

    # 获取该贴吧帖子数
    num =int((soup.find(class_='card_infoNum').text).replace(',',''))
    return num

def search_n_pages(name,count):
    '''爬取n页数据'''
    target = []
    sum = get_num(name)
    print('帖子数：',sum)
    if sum>50:
    # 发起n次的get请求
    #从aatxt获得上次执行的页数
        ia =get_i()
        for i in range(ia,sum//50):
            # 跟踪进度
            print('page:', i)

            # 按照浏览贴吧的自然行为，每一页50条
            target_url = template_url.format(name= name ,sum = 50*i)
            #为了获取能方便快点查阅每搞100次要重新执行可以设置
            # 获取该页帖子列表，每次搞100页
            #使用count动态设置好了
            if i%count !=0 :
                page_lst = get_page_lst(target_url)
            else:
                set_i(i+1)
                break

            # 该页信息保存到target
            target.extend(extra_from_one_page(page_lst))

            # 休息0.2秒再访问，友好型爬虫
            time.sleep(0.2)
        return target
    else:
        print('这贴吧不火···')
def data_to_excel(name,count):
    pd_data  = search_n_pages(name,count)
    data = pd.DataFrame(pd_data)
    data.to_excel(name+str(round(time.time()*1000))+'.xlsx')
def get_i():
    fl = open('aa.txt')
    i = int(fl.read())
    fl.close()
    return i
def set_i(i):
    try:
        fl = open('aa.txt','w')
        fl.truncate()
        fl.write(str(i))
        fl.close()
    except FileNotFoundError:
        print("有找到aa,txt文件")

data_to_excel("大主宰",5)
# -*- coding: utf-8 -*-
# @Author: longzx
# @Date: 2018-03-10 21:41:55
# @cnblog:http://www.cnblogs.com/lonelyhiker/

import requests
import sys
from bs4 import BeautifulSoup
from pymysql.err import ProgrammingError
from .spider_tools import get_one_page, update_fiction, insert_fiction, insert_fiction_content, insert_fiction_lst, \
    insert_fiction_list
from app.models import Fiction_Lst, Fiction_Content, Fiction, FictionListAll


def get_list_of_fiction(url):
    page = get_one_page(url)
    soup = BeautifulSoup(page, 'html5lib')
    # print soup
    div = soup.find_all('div', id='main')
    a = div[0].find_all('a')
    fiction_list = []
    for rec in a:
        fiction_name = rec.string
        fiction_url = rec['href']
        temp = {'fiction_name': fiction_name, 'fiction_url': fiction_url}
        fiction_list.append(temp)
    return fiction_list


# 获取全部小说
def set_all_list():
    url = 'http://www.xbiquge.la/xiaoshuodaquan/'
    fiction_list = get_list_of_fiction(url)
    for rec in fiction_list:
        insert_fiction_list(rec['fiction_name'], rec['fiction_url'])


# 获取小说图片信息等内容
def set_fiction_all(soup, fiction_name, fiction_url):
    div = soup.find_all('div', id='fmimg')
    info = soup.find_all('div', id='info')
    comment = soup.find_all('div', id='intro')

    fiction_id = fiction_url.split('/')[-2]
    fiction_img = div[0].find_all('img')[0]['src']
    fiction_author = info[0].find_all('p')[0].string.split('：')[-1]
    update = info[0].find_all('p')[2].string.split('：')[-1]
    new_url = info[0].find_all('p')[3].find_all('a')[0]['href']
    new_content = info[0].find_all('p')[3].find_all('a')[0].string
    fiction_comment = comment[0].find_all('p')[1].string

    insert_fiction(fiction_name, fiction_id, fiction_url, fiction_img,
                   fiction_author, fiction_comment, update, new_url, new_content)


def set_fiction_lst_all(soup, fiction_name, fiction_url):
    div = soup.find_all('div', class_='box_con')[1].find_all('div', id='list')

    lst = div[0].find_all('a')
    fiction_id = fiction_url.split('/')[-2]
    print(len(div))
    for rec in lst:
        fiction_lst_url = 'http://www.xbiquge.la' + rec['href']
        fiction_lst_name = rec.string
        insert_fiction_lst(fiction_name, fiction_id, fiction_lst_url,
                           fiction_lst_name, fiction_url)


def get_fiction_list(fiction_name, fiction_url, flag=1):
    # 获取小说列表
    fiction = Fiction().query.filter_by(fiction_name=fiction_name).first()
    if fiction is None:
        fiction_html = get_one_page(fiction_url, sflag=flag)
        soup = BeautifulSoup(fiction_html, 'html5lib')
        set_fiction_all(soup, fiction_name, fiction_url)
    fiction = Fiction().query.filter_by(fiction_name=fiction_name).first()
    if fiction is None:
        print('获取 {} 失败！！！'.format(fiction_name))
        raise Exception('小说 :{} 获取失败！！！'.format(name))
    return fiction


def get_fiction_lst(fiction_name, fiction_url, flag=1):
    fiction_lst = Fiction_Lst().query.filter_by(fiction_name=fiction_name).first()
    if fiction_lst is None:
        # 爬取所有章节
        fiction_html = get_one_page(fiction_url, sflag=flag)
        soup = BeautifulSoup(fiction_html, 'html5lib')
        set_fiction_lst_all(soup, fiction_name, fiction_url)


def search_fiction(name, flag=1):
    """输入小说名字

    返回小说在网站的具体网址
    """
    if name is None:
        raise Exception('小说名字必须输入！！！')

    fiction = FictionListAll().query.filter_by(fiction_name=name).first()

    # 如果没有找到，就去爬取所有小说
    if fiction is None:
        set_all_list()
        fiction = FictionListAll().query.filter_by(fiction_name=name).first()

    # 爬取完成之后还是没有就真的没有了
    if fiction is None:
        print('{} 小说不存在！！！'.format(name))
        raise Exception('{} 小说不存在！！！'.format(name))
    fiction_name = fiction.fiction_name
    fiction_url = fiction.fiction_url

    return fiction_name, fiction_url


def get_fiction_content(fiction_url, flag=1):
    fiction_id = fiction_url.split('/')[-2]
    # fiction_conntenturl = fiction_url.split('/')[-1].strip('.html')
    fc = Fiction_Content().query.filter_by(
        fiction_id=fiction_id, fiction_url=fiction_url).first()
    if fc is None:
        print('此章节不存在，需下载')
        html = get_one_page(fiction_url, sflag=flag)
        soup = BeautifulSoup(html, 'html5lib')
        content = \
        soup.find_all('div', class_='content_read')[0].find_all('div', class_='box_con')[0].find_all('div', id='content')[0]
        print(content.string)
        f_content = str(content.string)
        save_fiction_content(fiction_url, f_content)
    else:
        print('此章节已存在，无需下载！！！')


def save_fiction_lst(fiction_lst):
    total = len(fiction_lst)
    if Fiction().query.filter_by(fiction_id=fiction_lst[0][1]) == total:
        print('此小说已存在！！，无需下载')
        return 1
    for item in fiction_lst:
        insert_fiction_lst(*item)


def save_fiction_content(fiction_url, fiction_content):
    fiction_id = fiction_url.split('/')[-2]
    fiction_conntenturl = fiction_url.split('/')[-1].strip('.html')
    insert_fiction_content(fiction_conntenturl, fiction_content, fiction_id)


def down_fiction_lst(f_name):
    # 1.搜索小说
    fiction_name, fiction_url = search_fiction(f_name, flag=0)
    # 2.获取小说标题，图片等内容
    get_fiction_list(fiction_name, fiction_url)
    # 3.获取小说章节信息
    get_fiction_lst(fiction_name, fiction_url)

    print('下载小说列表完成！！')


def down_fiction_content(f_url):
    get_fiction_content(f_url, flag=0)
    print('下载章节完成！！')


def update_fiction_lst(f_name, f_url):
    # 1.获取小说目录列表
    fiction_lst = get_fiction_list(
        fiction_name=f_name, fiction_url=f_url, flag=0)
    # 2.保存小说目录列表
    flag = save_fiction_lst(fiction_lst)
    print('更新小说列表完成！！')

from concurrent.futures import ThreadPoolExecutor
from manage import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from app.models import Fiction_Lst, Fiction_Content, Fiction, FictionListAll, SpiderTask
from ..xiaoshuo.spider_tools import get_one_page
from bs4 import BeautifulSoup

some_engine = create_engine(
    app.config.get('SQLALCHEMY_DATABASE_URI', 'mysql+pymysql://zc:Zc123456.@localhost/blog?charset=utf8'))
session_factory = sessionmaker(bind=some_engine)
Session = scoped_session(session_factory)


class TaskThreadPool:
    def __init__(self, max_pool):
        self.thread_pool = ThreadPoolExecutor(max_workers=max_pool)

    def add_task(self, task, *para):
        result = self.thread_pool.submit(task, *para)
        return result


pool = TaskThreadPool(max_pool=4)


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


def set_all_list(session, fiction_list_all):
    list_map = dict()
    for rec in fiction_list_all:
        # print(rec, rec.fiction_name)
        list_map[rec.fiction_name] = 1
    print(list_map)
    url = 'http://www.xbiquge.la/xiaoshuodaquan/'
    fiction_list = get_list_of_fiction(url)
    print('获取成功')

    for rec in fiction_list:
        if rec['fiction_name'] in list_map:
            continue
        print('新增数据')
        fiction_list = FictionListAll(fiction_name=rec['fiction_name'], fiction_url=rec['fiction_url'])
        session.add(fiction_list)
    session.commit()
    print('结束获取')


def search_fiction(name, task_id):
    print(name)
    if name is None:
        raise Exception('小说名字必须输入！！！')
    session = Session()
    fiction = session.query(FictionListAll).filter_by(fiction_name=name).first()

    if fiction is None:
        fiction_list = session.query(FictionListAll).all()
        # print(fiction_list)
        set_all_list(session, fiction_list)
        fiction = FictionListAll().query.filter_by(fiction_name=name).first()
    res = True
    if fiction is None:
        res = False
    print('spider end')
    after_spider_task_status(task_id, res)
    return res


def before_spider_task_status(task_id):
    print('before task')
    session = Session()
    task = session.query(SpiderTask).filter_by(task_id=task_id).first()
    task.task_status = 'RUN'
    session.commit()


def after_spider_task_status(task_id, res):
    print('after task')
    session = Session()
    task = session.query(SpiderTask).filter_by(task_id=task_id).first()
    if res:
        task.task_status = 'SUCCESS'
    else:
        task.task_status = 'ERROR'
    session.commit()


def add_spider_task_pool(task_id, task, para):
    before_spider_task_status(task_id)
    pool.add_task(eval(task), para, task_id)

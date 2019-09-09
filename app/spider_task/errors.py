from .thread_pool_task import pool
from ..xiaoshuo.xiaoshuoSpider import search_fiction


def test_1(x):
    for i in range(100000):
        pass
    print(x, i)
    return x


if __name__ == '__main__':
    pool.add_task(search_fiction, '三寸人间')

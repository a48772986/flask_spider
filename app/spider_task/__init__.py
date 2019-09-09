from flask import Blueprint

# 实例化蓝本对象，必须指定name蓝本名字，import_name蓝本所在包或模块
spider_task = Blueprint(name='spider_task', import_name=__name__)

# 在这个位置导入是为了防止循环导入依赖问题
from . import views, errors, thread_pool_task

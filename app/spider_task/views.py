from . import spider_task
from flask import (current_app, make_response, redirect, render_template, jsonify,
                   request, url_for, flash, session)
from .forms import SpiderTask
from ..models import FictionListAll, db, SpiderTask as st
from .thread_pool_task import add_spider_task_pool
import json
from datetime import datetime


@spider_task.route('/spider_task')
def index():
    form = SpiderTask().get_all()

    return render_template('spider_task/spider_task.html', form=form)


@spider_task.route('/get_spider_task_all', methods=['post', 'get'])
def get_spider_task_all():
    data = st().query.all()
    print(json.loads(str(data)))
    return jsonify(json.loads(str(data)))


@spider_task.route('/add_spider_task', methods=['post'])
def add_spider_task():
    data = request.form
    print(data)
    task = st().query.filter_by(task_name=data.get('task_name')).first()
    if task is None:
        task = st(task_name=data.get('task_name'),
                  task_type=data.get('task_type'),
                  task_status=data.get('task_status'),
                  creation_date=str(datetime.now().date()))
        db.session.add(task)
        db.session.commit()
    return 'ok'


@spider_task.route('/run_task', methods=['post'])
def run_task():
    print(request.args, request.form, request.get_data(as_text=True))
    datas = json.loads(request.get_data(as_text=True))
    for data in datas:
        res = st().query.filter_by(task_id=data['task_id']).first()
        add_spider_task_pool(task_id=data['task_id'], task=res.task_type, para=res.task_name)
        # print(res)
        db.session.commit()
    res = {'status': 'SUCCESS'}
    return jsonify(res)

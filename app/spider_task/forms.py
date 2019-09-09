class SpiderTask:

    def __init__(self):
        self.task_id = {
            'field': 'task_id',
            'title': '任务id',
            'type': 'text'
        }

        self.task_name = {
            'field': 'task_name',
            'title': '任务名称',
            'type': 'text'
        }

        self.task_type = {
            'field': 'task_type',
            'title': '任务类型',
            'type': 'text'
        }

        self.task_status = {
            'field': 'task_status',
            'title': '任务状态',
            'type': 'text'
        }

        self.creation_date = {
            'field': 'creation_date',
            'title': '创建时间',
            'type': 'text'
        }

    def __str__(self):
        print(locals().items())
        for v in locals().items():
            print(v)
        return 'xxx'

    def get_all(self):
        return self.__dict__

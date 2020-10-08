from dj_celery_progress_sample import celery_app


class BaseTask(celery_app.Task):
    ignore_result = False

    def __call__(self, *args, **kwargs):
        print("Starting %s" % self.name)
        return self.run(*args, **kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # exit point of the task whatever is the state
        print("End of %s" % self.name)

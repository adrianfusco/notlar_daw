from gunicorn.app.base import BaseApplication
from notlar import app


class FlaskApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        for key, value in self.options.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run_gunicorn():
    options = {
        'bind': '0.0.0.0:5000',
        'workers': 4,
        # We can enable True for development
        'reload': True,
        'accesslog': '-',
        'errorlog': '-',
    }

    FlaskApplication(app, options).run()


if __name__ == '__main__':
    run_gunicorn()

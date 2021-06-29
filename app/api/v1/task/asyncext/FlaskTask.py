from flask import current_app

"""
Flask Task binding with app_context
"""
class FlaskTask():
    def __init__(self, fn, args):
        self.app = current_app._get_current_object()
        self.fn = fn
        self.args = args
    def __call__(self):
        with self.app.app_context():            
            self.fn(self.args)

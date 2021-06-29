import threading
from flask import Blueprint, current_app, request, render_template, jsonify, session, redirect 

"""
支持在线程中访问app_context的Thread
"""
class FlaskThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = current_app._get_current_object()
        
    def run(self):
        with self.app.app_context():
            super().run()

from py2neo import Graph

class Neo():
    def __init__(self):
        self.g = None

    def init_app(self, app):
        self.g = Graph(app.config['NEO4J_SETTINGS']['url'],
        username=app.config['NEO4J_SETTINGS']['username'],
        password=app.config['NEO4J_SETTINGS']['password'])        
        app.neo = self.g


import os

class basicConfig():
    SECRET_KEY = os.getenv("SECRET_KEY",'SECRET_KEY')
    CUCKOO_URL = os.getenv('CUCKOO_URL')
    MONGODB_SETTINGS = {
        'db': os.getenv('MONGO_DBNAME', 'mal'),
        'host': os.getenv('MONGO_HOST', 'mongo'),
        'port': os.getenv('MONGO_PORT',  27017),
        'username': os.getenv('MONGO_USERNAME', 'mongoadmin'),
        'password': os.getenv('MONGO_PASSWORD', 'mongoadmin'),
        'authentication_source': os.getenv('MONGO_AUTHDB', 'admin')
    }
    NEO4J_SETTINGS = {
        'url': os.getenv('NEO4J_URL', 'http://localhost:7474'),
        'username': os.getenv('NEO4J_USERNAME', 'neo4j'),
        'password': os.getenv('NEO4J_PASSWORD')
    }
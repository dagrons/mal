from .malware_classification.predict import predict as predict_cls
from .malware_sim.predict import predict as predict_sim


def analyze(bytes_path, bmp_path):
    
    res = None

    return predict_cls(bmp_path), predict_sim(bytes_path)
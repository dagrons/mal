from .basicConfig import basicConfig
from .developmentConfig import developmentConfig
from .productionConfig import productionConfig

config = {
    'development': developmentConfig,
    'production': productionConfig
}
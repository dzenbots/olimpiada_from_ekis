from .env_config import MayakConfig

config = MayakConfig.load()

__all__ = ['config', 'MayakConfig']

from .env_config import Config

config = Config.load()

__all__ = ['config', 'Config']

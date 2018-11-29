import multiprocessing
from typing import Dict, Any
from abc import ABC, abstractmethod
from json import loads, JSONDecodeError
from pathlib import Path


class Config(dict, ABC):
    @abstractmethod
    def __init__(self):
        self['mode'] = 'BASE'
        self['environment'] = {
            'home': '/opt/authark'
        }
        self['gunicorn'] = {
            'bind': '%s:%s' % ('0.0.0.0', '8080'),
            'workers': 1,
            'worker_class': 'gevent',
            'debug': False
        }
        self['flask'] = {}
        self['database'] = {}
        self['tokens'] = {
            'access_lifetime': 86400,
            'refresh_lifetime': 604800,
            'refresh_threshold': 86400
        }

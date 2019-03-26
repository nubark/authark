from pytest import fixture
from injectark import Injectark
from authark.infrastructure.config import TrialConfig
from authark.infrastructure.factories import build_factory


@fixture
def config():
    return TrialConfig()


@fixture
def resolver(config):
    factory = build_factory(config)
    strategy = config['strategy']
    resolver = Injectark(strategy=strategy, factory=factory)
    return resolver


@fixture
def context(config, registry):
    return Context(config, registry)

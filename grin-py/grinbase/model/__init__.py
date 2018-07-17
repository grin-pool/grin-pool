import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import inspect
import pkgutil
import importlib
import sys



Base = declarative_base()


def initialize_sql(engine):
    #print("Initializing session factory")
    global session_factory
    session_factory = sessionmaker(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)


def import_models():
    thismodule = sys.modules[__name__]

    sys.path.insert(0, os.path.dirname(__file__))
    for loader, module_name, is_pkg in pkgutil.iter_modules(
            thismodule.__path__, thismodule.__name__ + '.'):
        loaderp= None
        module = importlib.import_module(module_name, loaderp)
        for name, _object in inspect.getmembers(module, inspect.isclass):
            globals()[name] = _object

import_models()

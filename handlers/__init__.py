# handlers/__init__.py

from .convert import register_handlers as register_convert

def register_all_handlers(dp):
    # Register all handlers here
    register_convert(dp)

# handlers/__init__.py

from .convert import register_handlers as register_convert

def register_all_handlers(dispatcher):
    # Registering all the handlers (you can add more as needed)
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), register_convert))

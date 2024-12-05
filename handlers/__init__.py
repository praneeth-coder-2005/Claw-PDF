from .merge import register_handlers as register_merge
from .compress import register_handlers as register_compress
from .convert import register_handlers as register_convert

# Combine all handlers into a single function
def register_all_handlers(dp):
    register_merge(dp)
    register_compress(dp)
    register_convert(dp)

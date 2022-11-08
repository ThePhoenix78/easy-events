try:
    from .commands import *
    from .async_commands import *
except ImportError:
    from commands import *
    from async_commands import *

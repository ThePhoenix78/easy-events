try:
    from .commands import *
    from .async_commands import *
    from .objects import *
except ImportError:
    from commands import *
    from async_commands import *
    from objects import *

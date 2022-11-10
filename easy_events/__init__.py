try:
    from .commands import Commands
    from .async_commands import AsyncCommands
    from .objects import Parameters, Decorator, Event
except ImportError:
    from commands import Commands
    from async_commands import AsyncCommands
    from objects import Parameters, Decorator, Event

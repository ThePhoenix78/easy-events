try:
    from .events import Events
    from .async_events import AsyncEvents
    from .objects import Parameters, Decorator, Event
    from .simple_events import EasyEvents
except ImportError:
    from events import Events
    from async_events import AsyncEvents
    from objects import Parameters, Decorator, Event
    from simple_events import EasyEvents

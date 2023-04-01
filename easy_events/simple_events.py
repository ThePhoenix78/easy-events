from threading import Thread
import asyncio

try:
    from .easy_events import Events, AsyncEvents, Parameters
except ImportError:
    from easy_events import Events, AsyncEvents, Parameters


class EasyEvents():
    def __init__(self,
                 prefix: str = "",
                 str_only: bool = False,
                 use_funct_name: bool = True,
                 first_parameter_object: bool = True,
                 default_event: bool = True
                 ):

        self.sync = Events(prefix=prefix, str_only=str_only, use_funct_name=use_funct_name, first_parameter_object=first_parameter_object, default_event=False)
        self.asyn = AsyncEvents(prefix=prefix, str_only=str_only, use_funct_name=use_funct_name, first_parameter_object=first_parameter_object, default_event=False)
        self.str_only = str_only

        if default_event:
            self.event = self.add_event

    def trigger(self, data, event_type: str = None, str_only: bool = None, thread: bool = False):
        none = type(None)

        if isinstance(str_only, none):
            str_only = self.str_only

        data = Parameters(data, str_only=str_only)

        sync = self.sync.grab_event(name=data._event, event_type=event_type)
        asyn = self.asyn.grab_event(name=data._event, event_type=event_type)

        if thread:
            if asyn:
                Thread(target=self._execute_async, args=[data, event_type, str_only]).start()
            elif sync:
                Thread(target=self._execute, args=[data, event_type, str_only]).start()

            return

        if asyn:
            return self._execute_async(data=data, event_type=event_type, str_only=str_only)
        elif sync:
            return self._execute(data, event_type, str_only)

    def _execute_async(self, data, event_type: str = None, str_only: bool = None):
        return asyncio.run(self.asyn.trigger_run(data=data, event_type=event_type, str_only=str_only))

    def _execute(self, data, event_type: str = None, str_only: bool = None):
        return self.sync.trigger(data=data, event_type=event_type, str_only=str_only)

    def add_event(self, aliases: list = [], condition: callable = None, type: str = None, callback: callable = None, event_type: str = None):
        if isinstance(aliases, str):
            aliases = [aliases]

        if not callable(condition):
            condition = None

        def add_func(func):
            if asyncio.iscoroutinefunction(func):
                evt = self.asyn.add_event(callback=func, aliases=aliases, event_type=event_type, condition=condition)
            else:
                evt = self.sync.add_event(callback=func, aliases=aliases, event_type=event_type, condition=condition)

            aliases.clear()
            return evt

        if callable(callback):
            return add_func(callback)

        return add_func


if __name__ == "__main__":
    client = EasyEvents(first_parameter_object=False)

    @client.event()
    def test(a, b):
        print(a, b)

    @client.event()
    async def test2(a, b):
        print(a, b)

    client.trigger({"event": "test", "parameters": {"a": 1, "b": "b"}})
    client.trigger({"event": "test2", "parameters": {"a": 1, "b": "b"}})

    client.trigger("test2 hello world")
    client.trigger("test hello world")

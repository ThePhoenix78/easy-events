from threading import Thread
import asyncio

try:
    from .async_events import AsyncEvents
    from .events import Events
    from .objects import Parameters
except ImportError:
    from async_events import AsyncEvents
    from events import Events
    from objects import Parameters


class EasyEvents():
    def __init__(self,
                 prefix: str = "",
                 str_only: bool = False,
                 use_funct_name: bool = True,
                 default_event: bool = True,
                 default_context=None,
                 ):

        self.sync = Events(prefix=prefix, str_only=str_only, use_funct_name=use_funct_name, default_event=False, default_context=default_context)
        self.asyn = AsyncEvents(prefix=prefix, str_only=str_only, use_funct_name=use_funct_name, default_event=False, default_context=default_context)

        self.str_only = str_only
        self.prefix = prefix

        if default_event:
            self.event = self.add_event

    def trigger(self, data, parameters=None, event_type: str = None, context=None, str_only: bool = None, thread: bool = False):
        if isinstance(str_only, type(None)):
            str_only = self.str_only

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            data = Parameters(data=data, parameters=parameters, prefix=self.prefix, str_only=str_only)

        sync = self.sync.grab_event(name=data._event, event_type=event_type)
        asyn = self.asyn.grab_event(name=data._event, event_type=event_type)

        if thread:
            if asyn:
                Thread(target=self._execute_async, args=[data, event_type, context, str_only]).start()
            elif sync:
                Thread(target=self._execute, args=[data, event_type, context, str_only]).start()

            return

        if asyn:
            return self._execute_async(data=data, event_type=event_type, context=context, str_only=str_only)
        elif sync:
            return self._execute(data=data, event_type=event_type, context=context, str_only=str_only)

    def _execute_async(self, data, event_type: str = None, context=None, str_only: bool = None):
        return asyncio.run(self.asyn.trigger(data=data, event_type=event_type, context=context, str_only=str_only))

    def _execute(self, data, event_type: str = None, context=None, str_only: bool = None):
        return self.sync.trigger(data=data, event_type=event_type, context=None, str_only=str_only)

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

    async def run_task(self, thread: bool = False):
        self.sync.run_task(thread)
        await self.asyn.run_task()

    def run_task_sync(self, thread: bool = None, sync_thread: bool = False, async_thread: bool = False):
        if not isinstance(thread, type(None)):
            sync_thread = thread
            async_thread = thread

        self.sync.run_task(sync_thread)
        self.asyn.run_task_sync(async_thread)

    def add_task(self, data, parameters=None, event_type: str = None, context=None, str_only: bool = None):
        if isinstance(str_only, type(None)):
            str_only = self.str_only

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            data = Parameters(data=data, parameters=parameters, str_only=str_only)

        evs = self.sync.grab_event(data._event, event_type)
        eva = self.asyn.grab_event(data._event, event_type)

        if eva:
            self.asyn.add_task(data=data, event_type=event_type, context=context, str_only=str_only)

        elif evs:
            self.sync.add_task(data=data, event_type=event_type, context=context, str_only=str_only)

    def grab_event(self, event: str, event_type: str = None):
        evs = self.sync.grab_event(event, event_type)
        eva = self.asyn.grab_event(event, event_type)


if __name__ == "__main__":
    import time, random
    t = time.time()

    class CTX:
        def __init__(self, i):
            self.i = i

    client = EasyEvents()


    @client.event()
    def test(a, b):
        i = random.randint(3, 10)
        time.sleep(i)
        print("sync", a, b, i)


    @client.event()
    async def test2(a, b):
        i = random.randint(3, 10)
        await asyncio.sleep(i)
        print("async", a, b, i)


    @client.event()
    def test3(ctx, a, b):
        print("Sync CTX", ctx.i, a, b)

    @client.event()
    async def test4(ctx, a, b):
        print("Async CTX", ctx.i, a, b)


    client.add_task({"event": "test2", "parameters": {"a": 1, "b": "b"}})
    client.add_task({"event": "test", "parameters": {"a": 1, "b": "b"}})

    client.add_task("test2 hello world")
    client.add_task("test hello world")

    client.add_task(test3, "hello ctx", context=CTX(2))
    client.add_task("test4 hello ctx", context=CTX(1))


    client.run_task_sync(sync_thread=True, async_thread=True)

    print(int(time.time()-t))

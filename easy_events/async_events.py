from inspect import getfullargspec
from asyncio import (
    gather,
    wait_for,
    new_event_loop,
    iscoroutinefunction,
    run_coroutine_threadsafe,
    AbstractEventLoop,
    TimeoutError,
    Future
)
import asyncio

try:
    from .objects import Decorator, Parameters, Event
except ImportError:
    from objects import Decorator, Parameters, Event

# import json
# from types import SimpleNamespace
# x = json.loads(data, object_hook=lambda _d: SimpleNamespace(**_d))


class AsyncEvents(Decorator):
    def __init__(self,
                 prefix: str = "",
                 lock: bool = False,
                 use_funct_name: bool = True,
                 first_parameter_object: bool = True
                 ):
        Decorator.__init__(self, is_async=True, use_funct_name=use_funct_name)
        self.prefix = prefix
        self._lock = lock
        self._run = True
        # self._loop: AbstractEventLoop = new_event_loop()
        self.waiting_list = []
        self.process_data = self.trigger
        self.first_parameter_object = first_parameter_object

    async def build_arguments(self, function, arguments):
        values = getfullargspec(function)

        arg = values.args

        default = values.defaults
        ext_default = values.kwonlydefaults
        ext = None

        if not arg and not values.kwonlyargs:
            return None

        if self.first_parameter_object:
            arg.pop(0)

        if values.kwonlyargs:
            ext = values.kwonlyargs[0]
            arg.extend(values.kwonlyargs)

        para = {}

        if default:
            default = list(default)
            for i in range(-1, -len(default)-1, -1):
                para[arg[i]] = default[i]

        s = len(arg)
        dico = {}

        if ext:
            if not (isinstance(arguments, list) or isinstance(arguments, dict)):
                arguments = arguments.split()

            sep = len(arguments) - s + 1

            if not sep:
                sep = 1

            for i in range(s):
                key = arg[i]

                if key != ext:
                    if isinstance(arguments, list):
                        try:
                            dico[key] = arguments.pop(0)
                        except IndexError:
                            if key in para.keys():
                                dico[key] = para[key]

                    elif isinstance(arguments, dict):
                        try:
                            dico[key] = arguments[key]
                        except KeyError:
                            if key in para.keys():
                                dico[key] = para[key]

                else:
                    li = []
                    if isinstance(arguments, list):
                        for _ in range(sep):
                            try:
                                li.append(arguments.pop(0))
                            except IndexError:
                                pass

                    elif isinstance(arguments, dict):
                        try:
                            li.append(arguments[key])
                        except KeyError:
                            pass

                    if not li and ext_default and ext_default.get(key):
                        li = [ext_default[key]]

                    dico[key] = li

        elif s:
            if isinstance(arguments, list):
                dico = {key: value for key, value in zip(arg, arguments[0:s])}

            elif isinstance(arguments, dict):
                for key in arg:
                    try:
                        dico[key] = arguments[key]
                    except KeyError:
                        if key in para.keys():
                            dico[key] = para[key]
            else:
                dico = {key: value for key, value in zip(arg, arguments.split()[0:s])}

        return dico

    async def execute(self, event: Event, data: Parameters):
        com = event.event
        con = event.condition

        dico = await self.build_arguments(com, data._parameters)

        data._parameters = dico

        if (con and con(data)) or not con:
            if not isinstance(dico, dict):
                return await com()

            if self.first_parameter_object:
                return await com(data, **dico)

            return await com(**dico)

    def trigger(self, data, event_type: str = None, lock: bool = None):
        none = type(None)

        if isinstance(lock, none):
            lock = self._lock

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            args = Parameters(data, self.prefix, lock)

        event = self.grab_event(args._event, event_type)

        if isinstance(args._event, str) and event and args._called:
            self.waiting_list.append((event, args))

    async def trigger_run(self, data, event_type: str = None, lock: bool = None):
        none = type(None)

        if isinstance(lock, none):
            lock = self._lock

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            args = Parameters(data, self.prefix, lock)

        event = self.grab_event(args._event, event_type)

        if isinstance(args._event, str) and event and args._called:
            return await self.execute(event, args)

    async def run_task(self):
        tasks = []

        for data in self.waiting_list:
            tasks.append(asyncio.create_task(self.execute(*data)))

        for task in tasks:
            await task

        self.waiting_list.clear()

    async def _thread(self):
        while self._run:
            await self.run_task()
            await asyncio.sleep(.1)

    def run(self):
        asyncio.run(self._thread())


if __name__ == "__main__":

    client = AsyncEvents(first_parameter_object=False)

    @client.event()
    async def hello(*, world):
        # await asyncio.sleep(1)
        print(f"Hello {world}")
        return f"Hello {world}"

    def build_data(data):
        data.image = "png"
        data.file = "txt"


    data = Parameters("hello", client.prefix)
    build_data(data)
    data = client.trigger(data)
    # print(0, data)

    data = client.trigger({"event": "hello", "parameters": {"world": "world", "lol": "data"}})
    # print(1, data)

    data = client.trigger({"event": "hello", "parameters": ["world", "data"]})
    # print(2, data)

    data = client.trigger(["hello", "world", "data"])
    # print(3, data)

    data = client.trigger("hello world data4")
    # print(4, data)

    client.run()

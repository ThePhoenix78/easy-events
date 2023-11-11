from inspect import getfullargspec
from threading import Thread
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
                 str_only: bool = False,
                 use_funct_name: bool = True,
                 default_event: bool = True,
                 default_context=None,
                 ):

        Decorator.__init__(self, is_async=True, use_funct_name=use_funct_name, default_event=default_event)
        self.prefix = prefix
        self._str_only = str_only
        self._run = True
        # self._loop: AbstractEventLoop = new_event_loop()
        self.waiting_list = []
        self.process_data = self.trigger
        ctx = False
        self.default_context = default_context


    async def build_arguments(self, function, arguments, context=None):
        values = getfullargspec(function)

        if arguments._default:
            arguments = arguments._default
        else:
            delattr(arguments, "_default")
            arguments = arguments.__dict__

        if not arguments:
            arguments = []

        arg = values.args

        annotations = values.annotations

        default = values.defaults

        ext_default = values.kwonlydefaults

        ext = None

        if not arg and not values.kwonlyargs:
            return None

        if not isinstance(context, type(None)):
            arg.pop(0)

        if values.kwonlyargs:
            ext = values.kwonlyargs[0]
            arg.extend(values.kwonlyargs)

        para = {}

        if default:
            default = list(default)
            for i in range(-1, -len(default)-1, -1):
                para[arg[i]] = default[i]


        len_arg = len(arg)

        dico = {}

        if ext:
            sep = len(arguments) - len_arg + 1

            if not sep:
                sep = 1

            for i in range(len_arg):
                key = arg[i]

                if key != ext:
                    if isinstance(arguments, list):
                        val_type = annotations.get(key)
                        try:
                            temp_val = arguments.pop(0)
                        except Exception:
                            continue

                        temp = temp_val

                        if val_type:
                            try:
                                temp = val_type(temp_val)
                            except Exception:
                                pass
                        try:
                            dico[key] = temp
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
                            li = arguments[key]
                        except KeyError:
                            pass

                    if not li and ext_default and ext_default.get(key):
                        li = [ext_default[key]]

                    dico[key] = li

        elif len_arg:
            if isinstance(arguments, list):
                # dico = {key: value for key, value in zip(arg, arguments[0:len_arg])}

                for key, value in zip(arg, arguments[0:len_arg]):
                    val_type = annotations.get(key)
                    temp = value

                    if val_type:
                        try:
                            temp = val_type(value)
                        except Exception:
                            pass

                    dico[key] = temp


            elif isinstance(arguments, dict):
                for key in arg:
                    try:
                        dico[key] = arguments[key]
                    except KeyError:
                        if key in para.keys():
                            dico[key] = para[key]

        return dico

    async def execute(self, event: Event, arguments, context=None):
        com = event.event
        con = event.condition

        if isinstance(context, type(None)) and not isinstance(self.default_context, type(None)):
            try:
                context = self.default_context()
            except Exception:
                context = self.default_context

        dico = await self.build_arguments(com, arguments, context)

        if (con and con(arguments)) or not con:
            if not isinstance(dico, dict):
                return await com()

            if not isinstance(context, type(None)):
                return await com(context, **dico)

            return await com(**dico)

    async def trigger(self, data, parameters=None, event_type: str = None, context=None, str_only: bool = None, thread: bool = False):
        none = type(None)
        if isinstance(str_only, none):
            str_only = self._str_only

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            args = Parameters(data=data, parameters=parameters, prefix=self.prefix, str_only=str_only)

        event = self.grab_event(args._event, event_type)

        if isinstance(args._event, str) and event and args._called:
            if thread:
                loop = self.start_async_thread()
                self.submit_async_thread(self.execute(event, args._parameters, context), loop)
            else:
                return await self.execute(event, args._parameters, context)

    def add_task(self, data, parameters=None, event_type: str = None, context=None, str_only: bool = None):
        none = type(None)

        if isinstance(str_only, none):
            str_only = self._str_only

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            args = Parameters(data=data, parameters=parameters, prefix=self.prefix, str_only=str_only)

        event = self.grab_event(args._event, event_type)

        if isinstance(args._event, str) and event and args._called:
            self.waiting_list.append((event, args._parameters, context))

    async def run_task(self):
        tasks = []

        for data in self.waiting_list:
            tasks.append(asyncio.create_task(self.execute(*data)))

        for task in tasks:
            await task

        self.waiting_list.clear()

    def run_task_sync(self, thread: bool = False):
        if thread:
            Thread(target=self._exec).start()
        else:
            self._exec()

    def _exec(self):
        asyncio.run(self.run_task())

    def start_async_thread(self):
        loop = asyncio.new_event_loop()
        Thread(target=loop.run_forever).start()
        return loop

    def submit_async_thread(self, awaitable, loop):
        return asyncio.run_coroutine_threadsafe(awaitable, loop)

    def stop_async_thread(self, loop):
        loop.call_soon_threadsafe(loop.stop)

    async def _thread(self):
        while self._run:
            await self.run_task()
            await asyncio.sleep(.1)

    def run(self):
        asyncio.run(self._thread())


if __name__ == "__main__":

    client = AsyncEvents()

    @client.event()
    async def hello(*, world):
        await asyncio.sleep(1)
        print(f"Hello {world}")
        print("lol", "lol")

        return f"Hello {world}"

    def build_data(data):
        data.image = "png"
        data.file = "txt"


    data = Parameters("hello", client.prefix)
    build_data(data)
    data = client.add_task(data)
    # print(0, data)

    async def main():
        data = await client.trigger({"event": "hello", "parameters": {"world": "world", "lol": "data"}}, thread=True)
        # print(1, data)

        data = await client.trigger({"event": "hello", "parameters": ["world", "data"]}, thread=True)
        # print(2, data)

        data = await client.trigger(["hello", "world", "data"])
        # print(3, data)

        data = await client.trigger("hello world data4")
        # print(4, data)
        return

    asyncio.run(main())
    # client.run_task_sync()

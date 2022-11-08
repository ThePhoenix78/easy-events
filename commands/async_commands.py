from inspect import getfullargspec
from ast import literal_eval
from threading import Thread
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
# import json
# from types import SimpleNamespace
# x = json.loads(data, object_hook=lambda _d: SimpleNamespace(**_d))


class Parameters:
    def __init__(self, data, prefix: str = "", lock: bool = False):
        self._prefix = prefix
        self._called = True
        self.command = data
        self.parameters = ""

        if not lock:
            self.revert()
        else:
            self.convert()

    def convert(self):
        check = False
        blank_prefix = False
        com = self.command

        if isinstance(self._prefix, str):
            check = str(self.command).startswith(self._prefix)
            blank_prefix = False if self._prefix else True

        elif isinstance(self._prefix, list):
            for pre in self._prefix:
                if str(self.command).startswith(pre):
                    check = True

                if check and pre == "":
                    blank_prefix = True

        if check and not blank_prefix:
            try:
                self.command = com.lower().split()[0][1:]
                self.parameters = " ".join(com.split()[1:])
            except Exception:
                self.command = com.lower()
                self.parameters = ""

        elif check and blank_prefix:
            self.command = com.lower().split()[0]
            self.parameters = " ".join(com.split()[1:])

        self._called = check

    def revert(self):
        done = False
        try:
            data = {"command": "", "parameters": ""}

            if isinstance(self.command, str) or isinstance(self.command, bytes):
                data = literal_eval(self.command)

            elif isinstance(self.command, list):
                if self.command:
                    data["command"] = self.command[0]

                if len(self.command) > 1:
                    data["parameters"] = self.command[1:]

            else:
                data = self.command

            self.command = data.get("command")
            self.parameters = data.get("parameters")

            done = True

            for key, value in data.items():
                if key not in ["command", "parameters"]:
                    setattr(self, key, value)

        except Exception:
            if not done:
                self.convert()

    def transform(self):
        return self.__dict__

    def build_str(self):
        res = ""
        for key, value in self.__dict__.items():
            res += f"{key} : {value}\n"

        return res

    def __str__(self):
        return self.build_str()

    def setattr(self, key, value):
        setattr(self, key, value)


class Decorator:
    def __init__(self):
        self.commands = {}

    def command_exist(self, name: str):
        return self.commands.get(name)

    def get_commands(self):
        return self.commands.keys()

    def command(self, condition=None, aliases=None):
        if isinstance(aliases, str):
            aliases = [aliases]
        elif not aliases:
            aliases = []

        if not callable(condition):
            condition = None

        def add_command(command_funct):
            if not iscoroutinefunction(command_funct):
                raise 'Command must be async: "async def ..."'

            aliases.append(command_funct.__name__)
            for command in aliases:
                self.commands[command.lower()] = {"command": command_funct, "condition": condition}
            return command_funct

        return add_command


class AsyncCommands(Parameters, Decorator):
    def __init__(self, prefix: str = "", lock: bool = False):
        Decorator.__init__(self)
        self.prefix = prefix
        self._lock = lock
        self._run = True
        self._loop: AbstractEventLoop = new_event_loop()
        self.waiting_list = []

    async def build_arguments(self, function, arguments):
        values = getfullargspec(function)

        arg = values.args
        arg.pop(0)

        default = values.defaults
        ext_default = values.kwonlydefaults

        para = {}

        if default:
            default = list(default)
            for i in range(-1, -len(default)-1, -1):
                para[arg[i]] = default[i]

        ext = None

        if values.kwonlyargs:
            ext = values.kwonlyargs[0]
            arg.extend(values.kwonlyargs)

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

    async def execute(self, data: Parameters):
        com = self.commands[data.command].get("command")
        con = self.commands[data.command].get("condition")

        dico = await self.build_arguments(com, data.parameters)

        data.parameters = dico

        if (con and con(data)) or not con:
            return await com(data, **dico)

    def process_data(self, data, lock: bool = None):
        none = type(None)

        if isinstance(lock, none):
            lock = self._lock

        args = data

        if not isinstance(data, Parameters):
            args = Parameters(data, self.prefix, lock)

        if isinstance(args.command, str) and self.command_exist(args.command) and args._called:
            self.waiting_list.append(args)

    async def _thread(self):
        while self._run:
            tasks = []

            for data in self.waiting_list:
                tasks.append(asyncio.create_task(self.execute(data)))

            """
            for task in tasks:
                print(await task)
            """

            self.waiting_list.clear()
            await asyncio.sleep(.1)

    def run(self):
        asyncio.run(self._thread())


if __name__ == "__main__":
    import asyncio
    client = AsyncCommands(prefix="!")

    @client.command()
    async def hello(data, *, world, lol="lol"):
        await asyncio.sleep(1)
        return f"Hello {world} / {lol}"

    def build_data(data):
        data.image = "png"
        data.file = "txt"


    data = Parameters("!hello", client.prefix)
    build_data(data)
    data = client.process_data(data)
    print(0, data)

    data = client.process_data({"command": "hello", "parameters": {"world": "world", "lol": "data"}})
    print(1, data)

    data = client.process_data({"command": "hello", "parameters": ["world", "data"]})
    print(2, data)

    data = client.process_data(["hello", "world", "data"])
    print(3, data)

    data = client.process_data("!hello world data")
    print(4, data)

    data = client.process_data("!salut mdr 222")
    print(data)

    client.run()

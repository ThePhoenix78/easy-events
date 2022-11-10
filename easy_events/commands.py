# coding: utf-8
from inspect import getfullargspec
try:
    from .objects import *
except ImportError:
    from objects import *

# import json
# from types import SimpleNamespace
# x = json.loads(data, object_hook=lambda _d: SimpleNamespace(**_d))


class Commands(Decorator):
    def __init__(self,
                 prefix: str = "",
                 lock: bool = False
                 ):

        Decorator.__init__(self, is_async=False)
        self.prefix = prefix
        self._lock = lock

    def build_arguments(self, function, arguments):
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

    def execute(self, data: Parameters):
        event = self.get_event(data.command)
        com = event.event
        con = event.condition

        dico = self.build_arguments(com, data.parameters)
        
        for elem in ["command", "parameters", "_prefix", "_called"]:
            delattr(data, elem)

        if (con and con(data)) or not con:
            return com(data, **dico)

    def process_data(self, data, lock: bool = None):
        none = type(None)

        if isinstance(lock, none):
            lock = self._lock

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.async_commands.Parameters'>":
            args = Parameters(data, self.prefix, lock)

        if isinstance(args.command, str) and self.event_exist(args.command) and args._called:
            try:
                val = self.execute(args)
            except Exception as e:
                raise e
                return f"{type(e)}: {e}"

            if isinstance(val, Parameters):
                return val.transform()

            return val

        if isinstance(data, bytes):
            return data.decode()

        return data


if __name__ == "__main__":
    client = Commands()

    @client.event("event_name", type="event")
    def event_name(data):
        print("test1")
        print("data", data)

    @client.event("second_event")
    def test2(data, arg1, arg2, *, arg3):
        print("test2", arg1, arg2, arg3)
        print("data", data)

    client.process_data("event_name")
    client.process_data({"command": "second_event", "parameters": ["arg1", "arg2", "arg3", "arg4"]})
    client.process_data(Parameters("test1"))
    print(client.get_events_names("event"))
    print(client.get_types())

    data = Parameters("test1")
    data.client = "hello"
    client.process_data(data)

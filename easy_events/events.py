# coding: utf-8
from inspect import getfullargspec
from threading import Thread
import time
try:
    from .objects import Decorator, Parameters, Event
except ImportError:
    from objects import Decorator, Parameters, Event

# import json
# from types import SimpleNamespace
# x = json.loads(data, object_hook=lambda _d: SimpleNamespace(**_d))


class Events(Decorator):
    def __init__(self,
                 prefix: str = "",
                 str_only: bool = False,
                 use_funct_name: bool = True,
                 first_parameter_object: bool = True,
                 default_event: bool = True
                 ):

        Decorator.__init__(self, is_async=False, use_funct_name=use_funct_name, default_event=default_event)
        self.prefix = prefix
        self._str_only = str_only
        self.process_data = self.trigger
        self.waiting_list = []
        self.first_parameter_object = first_parameter_object

    def build_arguments(self, function, arguments):
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
                            li = arguments[key]
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

    def execute(self, event: Event, data: Parameters):
        com = event.event
        con = event.condition

        dico = self.build_arguments(com, data._parameters)

        for elem in ["_event", "_parameters", "_prefix", "_called"]:
            delattr(data, elem)

        if (con and con(data)) or not con:
            if not isinstance(dico, dict):
                return com()

            if self.first_parameter_object:
                return com(data, **dico)

            return com(**dico)

    def trigger(self, data, event_type: str = None, str_only: bool = None):
        none = type(None)

        if isinstance(str_only, none):
            str_only = self._str_only

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            args = Parameters(data, self.prefix, str_only)

        event = self.grab_event(args._event, event_type)

        if isinstance(args._event, str) and event and args._called:
            try:
                val = self.execute(event, args)
            except Exception as e:
                raise e
                return f"{type(e)}: {e}"

            if isinstance(val, Parameters):
                return val.transform()

            return val

        return data

    def add_task(self, data, event_type: str = None, str_only: bool = None):
        none = type(None)

        if isinstance(str_only, none):
            str_only = self._str_only

        args = data

        if isinstance(data, Parameters):
            pass
        elif not str(type(data)) == "<class 'easy_events.objects.Parameters'>":
            args = Parameters(data, self.prefix, str_only)

        event = self.grab_event(args._event, event_type)

        if isinstance(args._event, str) and event and args._called:
            self.waiting_list.append((event, args))

    def run_task(self, thread: bool = False):
        for data in self.waiting_list:
            if thread:
                Thread(target=self.execute, args=[*data]).start()
            else:
                self.execute(*data)

        self.waiting_list.clear()


if __name__ == "__main__":
    client = Events(first_parameter_object=False, str_only=False)

    @client.event()
    def test1(arg1, arg2="", *, arg3=""):
        print("test1", arg1, arg2, arg3)
        print("data")

    # @client.event()
    def test2():
        print("test2") # , arg1, arg2, arg3)
        print("data") # , data)

    # client.event(aliases="event_name", type="event", callback=test1)
    # client.event(callback=test2)

    client.trigger("test1 1 2 3")
    print("-"*50)

    client.trigger({"event": "test1", "parameters": {"arg1": "a1", "arg2": "a2", "arg3": ["a1", "a2"]}})
    client.trigger({"event": "test1", "parameters": [1, 2, 3, 4, 5]})

    client.trigger({"event": "test2", "parameters": ["arg1", "arg2", "arg3", "arg4"]})
    # client.trigger(Parameters("test1"))

    data = Parameters("event_name")
    data.client = "hello"
    client.trigger(data)

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
                 default_event: bool = True,
                 default_context=None,
                 ):

        Decorator.__init__(self, is_async=False, use_funct_name=use_funct_name, default_event=default_event)
        self.prefix = prefix
        self._str_only = str_only
        self.process_data = self.trigger
        self.waiting_list = []
        self.default_context = default_context

    def build_arguments(self, function, arguments, context=None):
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

    def execute(self, event: Event, arguments, context=None):
        com = event.event
        con = event.condition

        if isinstance(context, type(None)) and not isinstance(self.default_context, type(None)):
            try:
                context = self.default_context()
            except Exception:
                context = self.default_context

        dico = self.build_arguments(com, arguments, context)

        if (con and con(arguments)) or not con:
            if not isinstance(dico, dict):
                return com()

            if not isinstance(context, type(None)):
                return com(context, **dico)

            return com(**dico)

    def trigger(self, data, parameters=None, event_type: str = None, context = None, str_only: bool = None, thread: bool = False):
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
            try:
                if thread:
                    Thread(target=self.execute, args=[event, args._parameters, context]).start()
                    return
                else:
                    val = self.execute(event, args._parameters, context)
            except Exception as e:
                raise e
                return f"{type(e)}: {e}"

            if isinstance(val, Parameters):
                return val.transform()

            return val

        return data

    def add_task(self, data, parameters=None, event_type: str = None, context = None, str_only: bool = None):
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

    def run_task(self, thread: bool = False):
        for data in self.waiting_list:
            if thread:
                Thread(target=self.execute, args=[*data]).start()
            else:
                self.execute(*data)

        self.waiting_list.clear()


if __name__ == "__main__":

    class CTX:
        chat = "chat"

    client = Events(str_only=False, prefix="")

    @client.event()
    def test1(arg1: int, arg2: str = "4", *, arg3: str = "3"):
        print("test1", f"arg1={arg1} | {type(arg1)} /", f"arg2={arg2} | {type(arg2)} /", f"arg3={arg3} | {type(arg3)}")
        print("\n")


    @client.event()
    def test2(ctx):
        # print("test2", f"arg1={arg1}") #, arg2, arg3)
        print("test2", f"ctx={ctx.chat}")
        print("\n")

    # client.event(aliases="event_name", type="event", callback=test1)
    # client.event(callback=test2)
    print("EMPTY")
    client.trigger("test1 5")
    print("-"*50)
    print("FULL")
    client.trigger({"event": "test1", "parameters": {"arg1": "a1", "arg2": "a2", "arg3": ["a1", "a2"], "arg4": "a"}})
    print("-"*50)
    print("LIST")
    client.trigger({"event": "test1", "parameters": ["1", 2, "3", "4", "5"]})
    print("-"*50)
    print("STR")
    client.trigger({"event": "test1", "parameters": "1 2 3 4 5"})
    print("-"*50)
    print("LIST ONLY")
    client.trigger(["test1", "1", "2", "3", "4", "5"])
    print("-"*50)
    print("STR ONLY")
    client.trigger("test2 7", context=CTX)

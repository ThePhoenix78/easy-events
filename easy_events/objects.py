# coding: utf-8
from inspect import getargspec
from ast import literal_eval
from asyncio import iscoroutinefunction


class Para:
    def __init__(self, *args, **kwargs):
        self._default = None

        for k,v in kwargs.items():
            setattr(self, k, v)

        """
        for k, v in enumerate(args):
            setattr(self, f"_{k}", v)
        """
        if args:
            self._default = list(args)

    def build_str(self):
        res = ""
        for key, value in self.__dict__.items():
            res += f"{key} : {value}\n"

        return res


class Parameters:
    def __init__(self, data, parameters=None, prefix: str = "", str_only: bool = True, separator: str = " "):
        self._prefix = prefix
        self._called = True

        if callable(data):
            self._event = data.__name__
        else:
            self._event = data

        self._separator = separator
        self._parameters = Para()

        if isinstance(parameters, type(None)):
            if not str_only:
                self.revert()
            else:
                self.convert()
        else:
            self.convert_parameters(parameters)

    def convert_parameters(self, parameters):
        if isinstance(parameters, str):
            self._parameters = Para(*parameters.split(self._separator))

        elif isinstance(parameters, list):
            self._parameters = Para(*parameters)

        elif isinstance(parameters, dict):
            self._parameters = Para(**parameters)

    def convert(self):
        check = False
        blank_prefix = False
        com = self._event

        if isinstance(self._prefix, str):
            check = str(self._event).startswith(self._prefix)
            blank_prefix = False if self._prefix else True

        elif isinstance(self._prefix, list):
            for pre in self._prefix:
                if str(self._event).startswith(pre):
                    check = True

                if check and pre == "":
                    blank_prefix = True

        if check and not blank_prefix:
            temp_event = com.lower().split(self._separator)
            try:
                self._event = temp_event[0][1:]
                if len(temp_event) > 1:
                    self._parameters = Para(*com.split(self._separator)[1:])

            except Exception:
                self._event = com.lower()

        elif check and blank_prefix:
            temp_event = com.lower().split(self._separator)
            self._event = temp_event[0]

            if len(temp_event) > 1:
                self._parameters = Para(*com.split(self._separator)[1:])

        self._called = check


    def revert(self):
        done = False
        try:
            data = {"event": "", "parameters": ""}

            if isinstance(self._event, str) or isinstance(self._event, bytes):
                data = literal_eval(self._event)

            elif isinstance(self._event, list):
                if self._event:
                    data["event"] = self._event[0]

                if len(self._event) > 1:
                    data["parameters"] = Para(*self._event[1:])
                    self._parameters = data.get("parameters")

            else:
                data = self._event

            self._event = data.get("event")
            para = data.get("parameters")

            if isinstance(para, str):
                self._parameters = Para(*para.split(self._separator))
            elif isinstance(para, list):
                self._parameters = Para(*para)
            elif isinstance(para, dict):
                self._parameters = Para(**para)

            done = True

            for key, value in data.items():
                if key not in ["event", "parameters"]:
                    setattr(self, key, value)

        except Exception:
            if not done:
                self.convert()

    def transform(self):
        return self.__dict__

    def clear(self):
        keys = [k for k in self.__dict__.keys()]
        for key in keys:
            delattr(self, key)

        del(self.revert)
        del(self.convert)

    def clean(self):
        del(self._event)
        del(self._parameters)
        del(self._prefix)
        del(self._called)
        del(self._separator)
        del(self.revert)
        del(self.convert)

    def build_str(self):
        res = ""
        for key, value in self.__dict__.items():
            res += f"{key} : {value}\n"

        return res

    def get(self, key: str):
        getattr(self, key, None)

    def __str__(self):
        return self.build_str()

    def setattr(self, key, value):
        setattr(self, key, value)

    def delattr(self, key):
        delattr(self, key)


class Event:
    def __init__(self,
                 names: list,
                 event: callable,
                 condition: callable = None,
                 event_type: str = None
                 ):

        self.names = names
        self.event = event
        self.condition = condition
        self.type = event_type

    def check_type(self, event_type: str = None):
        if not event_type:
            return True

        return self.type == event_type


class Decorator:
    def __init__(self, is_async: bool = False, use_funct_name: bool = True, default_event: bool=True):
        self.events = []
        self.is_async = is_async
        self.use_funct_name = use_funct_name

        if default_event:
            self.event = self.add_event

    def event_exist(self, name: str):
        return name in self.get_all_events_names()

    def type_exist(self, name: str):
        return name in self.get_types()

    def get_all_events_names(self):
        liste = []
        for ev in self.events:
            for name in ev.names:
                liste.append(name)

        return liste

    def get_all_events_types(self):
        liste = []
        for ev in self.events:
            liste.append(ev.type)

        return liste

    def get_events_names(self, event_type: str = None):
        liste = []
        for ev in self.events:
            for name in ev.names:
                if ev.type == event_type:
                    liste.append(name)

        return liste

    def get_events_type(self, event_type: str = None):
        liste = []
        for event in self.events:
            if event_type == event.type:
                liste.append(event)

        return liste

    def get_types(self):
        liste = []
        for ev in self.events:
            liste.append(ev.type)

        liste = list(dict.fromkeys(liste))
        return liste

    def get_event(self, name: str):
        for event in self.events:
            if name in event.names:
                return event

    def grab_event(self, name: str, event_type: str = None):
        for event in self.events:
            if name in event.names and event_type == event.type:
                return event

    def remove_event(self, name: str, event_type: str = None):
        event = self.grab_event(name, event_type)
        if event:
            self.events.remove(event)

    def add_event(self, callback: callable = None, aliases: list = [], condition: callable = None, type: str = None, event_type: str = None):
        if isinstance(aliases, str):
            aliases = [aliases]

        if not callable(condition):
            condition = None

        if type:
            event_type = type

        def add_command(command_funct):
            if self.is_async and not iscoroutinefunction(command_funct):
                raise '[Error] Command must be async: "async def ..."'

            if self.use_funct_name:
                aliases.append(command_funct.__name__)

            al = list(dict.fromkeys(aliases))

            self.events.append(Event(al, command_funct, condition, event_type))
            return command_funct

        if callable(callback):
            return add_command(callback)

        return add_command


if __name__ == "__main__":
    print("FULL")
    data = Parameters({"event": "test1", "parameters": {"arg1": "a1", "arg2": "a2", "arg3": ["a1", "a2"]}}, prefix="", str_only=False)
    print(1, data._parameters.build_str())
    print("-"*50)
    print("LIST")
    data = Parameters({"event": "test1", "parameters": ["1", 2, "3", "4", "5"]}, prefix="", str_only=False)
    print(2, data._parameters.build_str())
    print("-"*50)
    print("STR")
    data = Parameters({"event": "test1", "parameters": "1 2 3 4 5"}, prefix="", str_only=False)
    print(3, data._parameters.build_str())
    print("-"*50)
    print("LIST ONLY")
    data = Parameters(["test1", "1", "2", 3, "4"], prefix="", str_only=False)
    print(4, data._parameters.build_str())
    print("-"*50)
    print("STR ONLY")
    data = Parameters("test1 1 2 3 4", prefix="", str_only=False)
    print(5, data._parameters.build_str())
    print("-"*50)
    data = Parameters("test1", [1, 2, 3, 4], prefix="", str_only=False)
    print(6, data._parameters.build_str())

    data = Parameters("test1", "1 2 3 4", prefix="", str_only=False)
    print(6, data._parameters.build_str())

    data = Parameters("test1", {"arg1": "a1", "arg2": "a2", "arg3": ["a1", "a2"]}, prefix="", str_only=False)
    print(6, data._parameters.build_str())

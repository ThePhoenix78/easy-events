# coding: utf-8
from ast import literal_eval
from asyncio import iscoroutinefunction


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

    def clear(self):
        keys = [k for k in self.__dict__.keys()]
        for key in keys:
            delattr(self, key)

    def clean(self):
        del(self.command)
        del(self.parameters)
        del(self._prefix)
        del(self._called)

    def build_str(self):
        res = ""
        for key, value in self.__dict__.items():
            res += f"{key} : {value}\n"

        return res

    def __str__(self):
        return self.build_str()

    def setattr(self, key, value):
        setattr(self, key, value)

    def delattr(self, key):
        delattr(self, key)


class Event:
    def __init__(self, 
                 names: list, 
                 event: str,
                 condition: callable = None,
                 event_type: str = None
                ):

        self.names = names
        self.event = event
        self.condition = condition
        self.type = event_type


class Decorator:
    def __init__(self, is_async: bool = False):
        self.events = []
        self.command = self.event
        self.is_async = is_async

    def event_exist(self, name: str):
        return name in self.get_events_names()

    def get_events_names(self, event_type: str = None):
        liste = []
        for ev in self.events:
            for name in ev.names:
                if not event_type:
                    liste.append(name)

                elif ev.type == event_type:
                    liste.append(name)

        return liste

    def get_types(self):
        liste = []
        for ev in self.events:
            liste.append(ev.type)

        liste = list(dict.fromkeys(liste))
        
        if None in liste:
            liste.remove(None)
        
        return  liste

    def get_events(self, event_type: str):
        liste = []
        for event in self.events:
            if not event_type:
                liste.append(event)

            elif event_type == event.type:
                liste.append(event)

        return liste

    def get_event(self, name: str):
        for event in self.events:
            if name in event.names:
                return event

    def event(self, aliases: list = None, condition: callable = None, type: str = None):
        if isinstance(aliases, str):
            aliases = [aliases]

        elif not aliases:
            aliases = []

        if not callable(condition):
            condition = None

        def add_command(command_funct):
            if self.is_async and not iscoroutinefunction(command_funct):
                raise 'Command must be async: "async def ..."'

            aliases.append(command_funct.__name__)
            al = list(dict.fromkeys(aliases))
            self.events.append(Event(al, command_funct, condition, type))
            return command_funct

        return add_command
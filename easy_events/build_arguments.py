from inspect import getfullargspec


def force_type(val_type: any, data: any):
    if val_type:
        try:
            data = val_type(data)
        except TypeError:
            if val_type is list:
                data: list = [data]
        except Exception:
            pass
    return data


def build_arguments(callback: callable, *_args, **_kwargs):
    values = getfullargspec(callback)
    _args: list = list(_args)

    print(_args, _kwargs)

    args = values.args

    annotations = values.annotations
    defaults = list(values.defaults)
    kwonlydefaults = values.kwonlydefaults
    kwonlyargs = values.kwonlyargs

    print(args, annotations, defaults, kwonlydefaults, kwonlyargs)

    if len(_args) < len(args) and len(defaults) < len(args):
        if isinstance(_args[0], str):
            _args: list = _args[0].split(" ", len(args))
        
        elif isinstance(_args[0], list):
            _args: list = _args[0]
        
        elif isinstance(_args[0], dict):
            _args: dict = _args[0]

    ext = None

    if not args and not kwonlyargs:
        return None

    if kwonlyargs:
        ext = kwonlyargs[0]
        args.extend(kwonlyargs)

    para: dict = {}

    if defaults:
        defaults = list(defaults)
        for i in range(-1, -len(defaults)-1, -1):
            para[args[i]] = defaults[i]

    len_arg: int = len(args)

    dico: dict = {}

    if ext:
        sep = len(_args) - len_arg + 1

        if not sep:
            sep = 1

        for i in range(len_arg):
            key = args[i]

            if key != ext:
                if isinstance(_args, list) and _args:
                    try:
                        temp = _args.pop(0)
                    except Exception:
                        continue

                    try:
                        dico[key] = temp
                    except IndexError:
                        if key in para.keys():
                            dico[key] = para[key]

                elif isinstance(_args, dict) and _args:
                    try:
                        dico[key] = _args[key]
                    except KeyError:
                        if key in para.keys():
                            dico[key] = para[key]

                elif _kwargs:
                    try:
                        dico[key] = _kwargs[key]
                    except KeyError:
                        if key in para.keys():
                            dico[key] = para[key]

            else:
                li = []
                if isinstance(_args, list) and _args:
                    for _ in range(sep):
                        try:
                            li.append(_args.pop(0))
                        except IndexError:
                            pass

                elif isinstance(_args, dict) and _args:
                    try:
                        li = _kwargs[key]
                    except KeyError:
                        pass             

                elif _kwargs:
                    try:
                        li = _kwargs[key]
                    except KeyError:
                        pass

                if not li and kwonlydefaults and kwonlydefaults.get(key):
                    li = [kwonlydefaults[key]]

                dico[key] = li

    elif len_arg:
        if isinstance(_args, list) and args:
            # dico = {key: value for key, value in zip(arg, arguments[0:len_arg])}

            for key, value in zip(args, _args[0:len_arg]):
                dico[key] = value

        elif isinstance(_args, dict) and args:
            for key in args:
                try:
                    dico[key] = _args[key]
                except KeyError:
                    if key in para.keys():
                        dico[key] = para[key]

        elif _kwargs:
            for key in args:
                try:
                    dico[key] = _kwargs[key]
                except KeyError:
                    if key in para.keys():
                        dico[key] = para[key]

    for key in args:
        if key not in dico.keys():
            if kwonlydefaults and kwonlydefaults.get(key):
                dico[key] = [kwonlydefaults[key]]

            if defaults:
                dico[key] = defaults.pop(0)

        val_type = annotations.get(key)
        dico[key] = force_type(val_type, dico[key])

    return dico

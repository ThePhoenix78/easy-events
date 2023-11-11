# easy-events

**A library that help you to manage events**

## Getting started

1. [**Installation**](#installation)
2. [**Usages**](#usages)
3. [**Code example**](#code-example)
4. [**Documentation**](#documentation)

## Installation

`pip install easy-events`

GitHub : [Github](https://github.com/ThePhoenix78/Commands)


## Usages

text

## Code example

```py
from easy_events import EasyEvents

# create an event or use it in a class
client = EasyEvents()


# create another event (can be sync or async)
# you can put as much parameters as you want
@client.add_event("test1")
def test(arg1, arg2, *, arg3):
	# data is the default parameter, it contain some basic informations that you can format as you want
	print(arg1, arg2, arg3)


# trigger the event
client.trigger(data=test1, parameters="arg1 arg2 arg3 arg4")
client.trigger("test1", "arg1 arg2 arg3 arg4")
client.trigger("test1", ["arg1", "arg2", "arg3", "arg4"])
client.trigger("test1", {"arg1": "arg1", "arg2": "arg2", "arg3": ["arg3", "arg4"]})

# dict way
client.trigger({"event": "test1", "parameters": {"arg1": "arg1", "arg2": "arg2", "arg3": ["arg3", "arg4"]}})

# dict way v2
client.trigger({"event": "test", "parameters": ["arg1", "arg2", "arg3", "arg4"]})

# dict way v3
client.trigger({"event": "test1", "parameters": "arg1 arg2 arg3 arg4"})

# list way
client.trigger(["test", "arg1", "arg2", "arg3", "arg4"])

# str way
client.trigger("test arg1 arg2 arg3 arg4")

# the result will be (for all cases):
# arg1 = arg1
# arg2 = arg2
# arg3 = [arg3, arg4]

```

### This library also support type assignation

```py
from easy_events import EasyEvents

client = EasyEvents()


@client.add_event()
def sum(X: int, Y: int):
	return X+Y


client.trigger("sum 5 10")
client.trigger(["sum", "5", 10])
# the result will be 15
```


### Context support


```py
from easy_events import EasyEvents


class CTX:
	def __init__(self, data: int = 0):
		self.data = data


client = EasyEvents(default_context=CTX)
# client = EasyEvents(default_context=CTX(0)) works as well

@client.add_event()
def context(ctx):
	print("ctx.data = ", ctx.data)


client.trigger("context", context=CTX(1))
client.trigger("context")

# this will print :
# "ctx.data = 1"
# "ctx.data = 0"
```

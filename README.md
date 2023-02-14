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
from easy_events import Events

# create an event or use it in a class
client = Events()


# create another event
# you can put as much parameters as you want
@client.event("test1")
def test(data, arg1, arg2, *, arg3):
	# data is the default parameter, it contain some basic informations that you can format as you want
	print(data, arg1, arg2, arg3)


# trigger the event

# dict way
client.trigger({"event": "test1", "parameters": {"arg1": "a1", "arg2": "a2", "arg3": ["arg3", "arg4"]}})

# dict way v2
client.trigger({"event": "test", "parameters": ["arg1", "arg2", "arg3", "arg4"]})

# list way
client.trigger(["test", "arg1", "arg2", "arg3", "arg4"])

# str way
client.trigger("test arg1 arg2 arg3 arg4")

# the result will be (for all cases):
# arg1 = arg1
# arg2 = arg2
# arg3 = [arg3, arg4]

```

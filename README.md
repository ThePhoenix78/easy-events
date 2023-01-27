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

# create an event
@client.event("event_name")
def test1(data):
	do_action_here


# trigger the event
client.trigger("event_name")

# create another event
# you can put as much parameters as you want
@client.event("second_event")
def test1(data, arg1, arg2, *, arg3):
	# data is the default parameter, it contain some basic informations that you can format as you want
	do_action_here


# trigger the event
client.trigger({"event": "second_event", "parameters": ["arg1", "arg2", "arg3", "arg4"]})
# here the parameters will be :
# arg1 = arg1
# arg2 = arg2
# arg3 = [arg3, arg4]

```

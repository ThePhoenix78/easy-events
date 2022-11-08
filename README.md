# easy-events

## 

### Installation

`pip install easy-events`

### Code example

```py
from commands import Commands

# create an event or use it in a class
client = Commands()

# create an event
@client.event("event_name")
def test1():
	do_action_here


# trigger the event
client.process_data("event_name")

# create another event
# you can put as much parameters as you want
@client.event("second_event")
def test1(data, arg1, arg2, *, arg3):
	# data is the default parameter, it contain some basic informations that you can format as you want
	do_action_here


# trigger the event
client.process_data({"command": "second_event", "parameters": ["arg1", "arg2", "arg3", "arg4"]})
# here the parameters will be : 
# arg1 = arg1
# arg2 = arg2
# arg3 = [arg3, arg4]

```
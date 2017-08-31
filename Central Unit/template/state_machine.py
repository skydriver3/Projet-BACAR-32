"""This is a template for State Machine Modules

   A State Machine module is a python file that contains a  `loop` function.
   Similar to how an Arduino program operates, `loop` is called continuously:
   when the function terminates, it is called again.

   The `loop` function should continuously listens to messages generated by:
   - the path detector (concerning the path to follow),
   - the sign detector (concerning road signs detected, if any),
   - the remote command operator (concerning commands to start/stop driving, or do specific manoeuvers)
   - and the arduino controller of the physical car (concerning the current state; possible sensor readings, ...)

   and decide on how to drive the car correspondingly. See the description of the
   `loop` method below for more details.
"""

import logging
import time
from event import Event
from car import Car


# constants for the different states in which we can be operating
IDLE = 1
STOPPED = 2
# You can add other states here





# Setup up the state machine. The following code is called when the state
# machine is loaded for the first time.
logging.info('Template StateMachine has been initialized')

# The next variable is a global variable used to store the state between
# successive calls to loop()
state = IDLE 


def loop():
    '''State machine control loop.
    Like an arduino program, this function is called repeatedly: whenever
    it exits it is called again. Inside the function, call:
    - time.sleep(x) to sleep for x seconds (x can be fractional)
    - Event.poll() to get the next event (output of Path and/or Sign detector,
      status sent by the car, or remote command).
    - Car.send(x,y,u,v) to communicate two integers (x and y) and
      two floats(u,v) to the car. How the car interprets this message depends
      on how you implement the arduino nano. For the simulator, x, and y
      are ignored while u encodes the speed and v the relative angle to turn
      to.
    '''
    global state  #define state to be a global variable
    event = Event.poll()
    if event is not None:
        if event.type == Event.CMD and event.val == "GO":
            # A command by the remote computer to start the car
            logging.info("remotely ordered to GO!")
            # TODO: here you would change status, and actuate car if necessary
        elif event.type == Event.CMD and event.val == "STOP":
            logging.info("remotely ordered to stop")
            # TODO: here you would order to car to stop immediately, and go to stop state
        #Note that you can decide to act on  other evant.val value for events of type Event.CMD!
        elif event.type == Event.PATH:
            # You received the PATH dictionary emitted by the path detector
            # you can access this dictionary in event.val
            # actuate car coresspondingly, change state if relevant
            pass
        elif event.type == Event.SIGN:
            # You received the SIGN dictionary emitted by the sign detector
            # you can access this dictionary in event.val
            # actuate car coresspondingly, change state if relevant
            pass
        elif event.type == Event.CAR:
            # You received a message from the arduino that is operating the car.
            # In this case, event.val contains a dictionary with keys x,y,u,v
            # where x and y are ints; u,v, are floats.
            # Act on this message depending on how you implemented the arduino
            # (e.g., is the arduino sending that there is an obstacle in front
            # and you should stop ?)
            pass

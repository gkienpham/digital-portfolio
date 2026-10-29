# ===== Project 10 Haunted House: Hub A (Dropper) =====
# When the skull (Hub B) starts a show, this hub runs the dropper on its own clock:
#   5 s -> platforms drop -> 5 s -> pull the knife up 33.5 turns -> 2 s
#   -> platforms close -> unwind at full speed (knife rests on the platforms again)
# Then it tells the skull it is ready for the next show.
# LEFT button: ask the skull to start a full show (for testing without the ball).
# Before starting: platforms closed, knife resting on them with slack in the string.
# Screen: check mark = hearing both other hubs, X = missing one (console says which).
# Start from the REPL / mpremote run, not the SPIKE App's Run button.
from spikecomm import Beacon, Scanner
from hub import port, button, light_matrix
import motor
import time

ME = "A"                # this hub
OTHERS = ["B", "C"]     # the hubs to listen to
LOST_MS = 1500          # nothing heard from a hub for this long = lost

# ----- Settings (tune these while testing) -----
RIGHT_PLATFORM = port.F     # medium motor
LEFT_PLATFORM = port.B      # medium motor
PULL_MOTOR = port.A         # large motor at the top
RIGHT_DROP = 90             # degrees to drop: + = clockwise
LEFT_DROP = -90             # degrees to drop: - = anticlockwise
DROP_SPEED = 800            # degrees per second (fast, for the surprise)
CLOSE_SPEED = 300           # degrees per second (gentle, under the knife)
CLOSE_MS = 700              # time to let the platforms close before unwinding
PULL_SPEED = 800            # degrees per second: + = clockwise = pull up
PULL_TURNS = 33.5           # motor turns to pull up (360 degrees each)
RELEASE_SPEED = 1050        # degrees per second (the large motor's max) to unwind
WAIT_BEFORE_DROP_MS = 5000  # after the skull sees the ball
WAIT_BEFORE_PULL_MS = 5000  # after the drop
WAIT_BEFORE_CLOSE_MS = 2000 # after the knife is pulled up

state = 0               # 0 = idle, 1 = running the dropper, 2 = test button asked the skull for a show
count = 0               # +1 every time the dropper finishes ("ready")

# latest["B"] = {"values": [state, count], "time": when it was heard}
latest = {}
for name in OTHERS:
    latest[name] = {"values": None, "time": 0}


def make_listener(name):
    """Make a callback that saves what hub `name` broadcasts."""
    def on_data(values):
        if len(values) == 2:            # [state, count]; ignore anything else
            latest[name]["values"] = values
            latest[name]["time"] = time.ticks_ms()
    return on_data


me = Beacon("!" + ME)
for name in OTHERS:
    Scanner("!" + name).listen(make_listener(name))
print("Hub", ME, "ready, listening for", OTHERS)

seen = {}               # last count seen from each other hub


def new_event(name):
    """True when hub `name`'s count just went up. The first count heard from a
    hub is only remembered, so starting or restarting a hub isn't an event."""
    values = latest[name]["values"]
    if values is None:
        return False
    is_new = name in seen and values[1] > seen[name]
    seen[name] = values[1]
    return is_new


screen = {"shown": None}


def show_link():
    """Check mark when both other hubs were heard lately, X when not."""
    now = time.ticks_ms()
    missing = []
    for name in OTHERS:
        if latest[name]["values"] is None or time.ticks_diff(now, latest[name]["time"]) > LOST_MS:
            missing.append(name)
    want = "lost" if missing else "ok"
    if want != screen["shown"]:
        if want == "ok":
            light_matrix.show_image(light_matrix.IMAGE_YES)
            print("Hearing", OTHERS)
        else:
            light_matrix.show_image(light_matrix.IMAGE_NO)
            print("Not hearing", missing)
        screen["shown"] = want


def wait_ms(ms):
    """Wait, keeping the screen up to date (Bluetooth keeps working too)."""
    end = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        show_link()
        time.sleep_ms(20)


was_pressed = False
while True:
    # Test button: count each press once, not while it's held
    pressed = bool(button.pressed(button.LEFT))
    test_run = pressed and not was_pressed
    was_pressed = pressed

    if test_run and state == 0:
        state = 2                       # the skull starts the show, like a ball hit
        print("Test button: asking the skull to start a show")

    if new_event("B"):
        print("Skull hit! Dropping in", WAIT_BEFORE_DROP_MS // 1000, "s")
        state = 1
        me.broadcast(state, count)
        wait_ms(WAIT_BEFORE_DROP_MS)

        print("Drop")                   # both platforms start together
        motor.run_for_degrees(RIGHT_PLATFORM, RIGHT_DROP, DROP_SPEED)
        motor.run_for_degrees(LEFT_PLATFORM, LEFT_DROP, DROP_SPEED)
        wait_ms(WAIT_BEFORE_PULL_MS)

        print("Pull up")                # HOLD keeps the knife up afterwards
        string_start = motor.relative_position(PULL_MOTOR)
        pull_degrees = int(PULL_TURNS * 360)
        motor.run_for_degrees(PULL_MOTOR, pull_degrees, PULL_SPEED, stop=motor.HOLD)
        wait_ms(pull_degrees * 1000 // PULL_SPEED + 500 + WAIT_BEFORE_CLOSE_MS)   # + 0.5 s to speed up and stop

        print("Close platforms")        # the opposite way of the drop
        motor.run_for_degrees(RIGHT_PLATFORM, -RIGHT_DROP, CLOSE_SPEED)
        motor.run_for_degrees(LEFT_PLATFORM, -LEFT_DROP, CLOSE_SPEED)
        wait_ms(CLOSE_MS)

        # Unwind exactly as much string as was pulled up, at full speed,
        # lowering the knife onto the platforms
        pulled = abs(motor.relative_position(PULL_MOTOR) - string_start)
        print("Unwind", pulled, "degrees")
        motor.run_to_relative_position(PULL_MOTOR, string_start, RELEASE_SPEED)
        wait_ms(pulled * 1000 // RELEASE_SPEED + 500)   # + 0.5 s to speed up and stop

        state = 0
        count += 1
        print("Ready for the next show")
    me.broadcast(state, count)          # does nothing if the data didn't change
    show_link()
    time.sleep_ms(20)

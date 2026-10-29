# ===== Project 10 Haunted House: Hub C (Slide) =====
# When the skull (Hub B) starts a show, push the next candy down the slide:
# one full turn (360 degrees) anticlockwise, ending back where it started.
# LEFT button: start a show without the ball (for testing).
# Before starting: put the pusher in its starting position.
# Screen: check mark = hearing both other hubs, X = missing one (console says which).
# Start from the REPL / mpremote run, not the SPIKE App's Run button.
from spikecomm import Beacon, Scanner
from hub import port, button, light_matrix
import motor
import time

ME = "C"                # this hub
OTHERS = ["A", "B"]     # the hubs to listen to
LOST_MS = 1500          # nothing heard from a hub for this long = lost

# ----- Settings (tune these while testing) -----
PUSHER = port.A
PUSH = -360             # degrees: - = anticlockwise; a full turn ends where it started
PUSH_SPEED = 300        # degrees per second

state = 0               # always 0 (this hub only reports button presses)
count = 0               # +1 for every LEFT press (test trigger)

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


was_pressed = False
while True:
    # Test button: count each press once, not while it's held
    pressed = bool(button.pressed(button.LEFT))
    if pressed and not was_pressed:
        count += 1
        print("Test button: asking the skull to start a show")
    was_pressed = pressed
    me.broadcast(state, count)          # does nothing if the data didn't change

    if new_event("B"):
        print("Candy push")
        motor.run_for_degrees(PUSHER, PUSH, PUSH_SPEED)

    show_link()
    time.sleep_ms(20)

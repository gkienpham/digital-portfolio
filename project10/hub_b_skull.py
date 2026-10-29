# ===== Project 10 Haunted House: Hub B (Skull) =====
# Watches the two color sensors in the skull's eyes. One azure reading on
# either sensor (the ball only flashes past) starts a show: the count goes up,
# the slide (Hub C) pushes candy and the dropper (Hub A) runs its timeline.
# LEFT on Hub C starts a show the same way (for testing without the ball).
# Hits are ignored until the dropper says it's ready again (or 60 s pass).
# Screen: check mark = hearing both other hubs, X = missing one (console says which).
# Start from the REPL / mpremote run, not the SPIKE App's Run button.
from spikecomm import Beacon, Scanner
from hub import port, light_matrix
import color
import color_sensor
import time

ME = "B"                # this hub
OTHERS = ["A", "C"]     # the hubs to listen to
LOST_MS = 1500          # nothing heard from a hub for this long = lost

# ----- Settings (tune these while testing) -----
EYES = {"B": port.B, "D": port.D}   # color sensors, by port letter
RESET_TIMEOUT_MS = 60000    # re-arm anyway if the dropper never says ready

state = 0               # 0 = armed (waiting for the ball), 1 = show running
count = 0               # +1 every time a show starts

# latest["A"] = {"values": [state, count], "time": when it was heard}
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


started = 0             # when the current show started
print("Armed: throw the ball!")
while True:
    test_pressed = new_event("C")       # check both every loop, so a press or
    dropper_ready = new_event("A")      # "ready" during a show isn't saved for later

    if state == 0:
        hit = None
        if test_pressed:
            hit = "test button on Hub C"
        for letter in EYES:
            if color_sensor.color(EYES[letter]) == color.AZURE:
                hit = "azure on sensor " + letter
        if hit:
            state = 1
            count += 1
            started = time.ticks_ms()
            print("Show", count, "started:", hit)
    elif dropper_ready:
        state = 0
        print("Dropper is ready. Armed: throw the ball!")
    elif time.ticks_diff(time.ticks_ms(), started) > RESET_TIMEOUT_MS:
        state = 0
        print("No ready from the dropper after", RESET_TIMEOUT_MS // 1000, "s. Armed anyway")

    me.broadcast(state, count)          # does nothing if the data didn't change
    show_link()
    time.sleep_ms(5)                    # check fast: the ball only flashes past

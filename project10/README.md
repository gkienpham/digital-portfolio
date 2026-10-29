# Project 10: Haunted House — hub code

Three SPIKE Prime hubs talk to each other over Bluetooth with
[spikecomm](https://github.com/edanahy/spikecomm) (v1.2.0, Beacon mode).

| Hub | Part | Ports | Program |
|---|---|---|---|
| A | Dropper | F right platform, B left platform, A top pull-up motor | `hub_a_dropper.py` |
| B | Skull | B and D color sensors (in the eyes) | `hub_b_skull.py` |
| C | Candy slide | A pusher motor | `hub_c_slide.py` |

Photos: `skull.jpg`, `dropper.jpg`.

## The show

1. The azure ball hits a skull eye. One azure reading on either sensor is enough.
2. Right away, the slide pushes one candy (one full anticlockwise turn, back to its start).
3. 5 s later, both platforms turn 90° and the knife drops.
4. 5 s after the drop, the top motor pulls the knife up 33.5 motor turns (about 15 s).
5. 2 s later, the platforms close. Then the top motor unwinds the same amount
   of string at full speed, so the knife rests on the platforms again.
6. The skull is armed again for the next throw (about 40 s per show). If the
   dropper doesn't answer, the skull re-arms after 60 s anyway.

**Test without the ball:** press LEFT on Hub C to start a show.
Pressing LEFT on Hub A does the same.

## How the hubs talk

Each hub broadcasts `state;count` and listens to the other two. `count` goes
up by 1 every time that hub's event happens, and the other hubs react when they
see it go up:

- Skull (`!B`) count up: a show started. The slide pushes candy and the dropper runs.
- Dropper (`!A`) count up: the dropper finished, so the skull re-arms.
- Slide (`!C`) count up: the test button was pressed, so the skull starts a show.

## Before starting

- Platforms closed, knife resting on them with slack in the string.
- Candy pusher in its starting position (every push is one full turn back to it).

## One-time setup

1. Install mpremote on the computer: `pip install mpremote`
2. Close the SPIKE App. Turn on **one** hub and plug it in with USB.
3. Copy the library onto it (run from the `project10` folder):
   `mpremote cp spikecomm.py :spikecomm.py`
4. Check it: `mpremote exec "import spikecomm; print(spikecomm.__version__)"` prints `1.2.0`.
5. Repeat for the other two hubs.

## Running the programs

Programs that use Bluetooth must be started from the computer, **not** with
the SPIKE App's Run button or the hub's menu.

1. Plug in Hub A and run `mpremote run hub_a_dropper.py`
2. Wait a second, then unplug the cable. The program keeps running on battery.
3. Do the same for Hub B (`hub_b_skull.py`) and Hub C (`hub_c_slide.py`).

To stop a hub, plug it back in and press Ctrl-C (or turn the hub off).

Screens: **✓** means the hub hears both other hubs, **✗** means it's missing one.

## Tuning

Speeds, times, angles and ports are listed under `Settings` at the top of
each program. If a motor turns the wrong way, flip the sign of its setting
(for example `RIGHT_DROP = 90` to `-90`).

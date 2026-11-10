# 1D Color Search: reinforcement learning on SPIKE Prime

A color sensor on a swinging arm scans a row of LEGO bricks. The robot uses
Q-learning to find the green brick without running into the black bricks at
either end. It starts knowing nothing about the track.

Run on 2026-11-09 on Hub B (the hub that was the Project 10 skull), rewired for this
activity.

## Where the code comes from

Both programs are **unmodified copies** from the professor's repository,
[edanahy/RLwithSPIKE](https://github.com/edanahy/RLwithSPIKE) (commit
`ead11c8`), by Ethan Danahy and the Tufts CEEO. They are MIT licensed, so
`LICENSE` is copied here too.

| File | What it is |
|---|---|
| `read_color.py` | Setup checker: prints what the sensor reads for every brick |
| `rl_color_search.py` | The Q-learning program |
| `logs/read_color_run.txt` | Everything the hub printed while I checked the track |
| `logs/rl_color_search_run.txt` | Everything the hub printed during training |

The logs are the hub's own output. Lines starting with `@` are data for the
professor's web dashboard. Each log ends where the USB cable disconnected.

## Hardware

| Port | Device |
|---|---|
| B | Large motor (the arm) |
| D | Color sensor (on the end of the arm, facing the bricks) |

The first try failed with `OSError: [Errno 19] ENODEV` because the hub was
still wired from Project 10 (only a large motor on port D, no color sensor).
After rewiring to the ports above, both programs ran.

## Settings

All settings were left at the defaults in the programs:

- Goal **GREEN**, boundary **BLACK**, no ignored colors
- Rewards: goal +10, boundary −10, every other move −1
- Learning rate α = 0.5, discount γ = 0.9, exploration ε = 0.1
- Arm speed 30°/s, 4 matching readings = a brick, at most 15 moves per episode

## How I ran it

Each program was started from the computer over USB:

```
mpremote connect /dev/cu.usbmodem3367395933381 soft-reset run read_color.py
mpremote connect /dev/cu.usbmodem3367395933381 soft-reset run rl_color_search.py
```

- **read_color.py:** hold LEFT or RIGHT on the hub to sweep the arm.
- **rl_color_search.py:** move the arm by hand to a starting brick, then
  RIGHT = train one episode, LEFT = test, center = end the program.

## Results

### Track check (read_color.py)

Three full sweeps from one black end to the other all read the same track:

```
BLACK  MAGENTA  YELLOW  BLUE  RED  GREEN  BLACK
```

Every gap between bricks read `NONE`, so no settings had to change.

### Training (rl_color_search.py)

12 training episodes. Episode 2 (from magenta) and episode 4 (from yellow) hit
the black end; the other 10 found green.

| Episode | Start | Steps | Result | Total reward |
|---|---|---|---|---|
| 1 | BLUE | 4 | goal | +7 |
| 2 | MAGENTA | 1 | boundary | −10 |
| 3 | RED | 1 | goal | +10 |
| 4 | YELLOW | 2 | boundary | −11 |
| 5 | YELLOW | 7 | goal | +4 |
| 6 | MAGENTA | 6 | goal | +5 |
| 7 | BLUE | 4 | goal | +7 |
| 8 | MAGENTA | 4 | goal | +7 |
| 9 | YELLOW | 3 | goal | +8 |
| 10 | MAGENTA | 6 | goal | +5 |
| 11 | BLUE | 2 | goal | +9 |
| 12 | MAGENTA | 4 | goal | +7 |

Episodes 3, 8, 9, 11 and 12 took the shortest possible path. Episodes 7 and 10
had random exploring moves that added extra steps.

Q-table after 12 episodes (higher = better move):

| Brick | LEFT | RIGHT | Best move |
|---|---|---|---|
| BLUE | 7.92 | −1.09 | LEFT |
| YELLOW | 5.50 | −0.90 | LEFT |
| RED | 9.99 | 2.24 | LEFT |
| MAGENTA | 2.55 | −7.50 | LEFT |

Green is at the LEFT end of the track, so LEFT is the right move from every
brick. The scores drop the farther a brick is from green, because every extra
move costs −1 and future rewards are discounted by γ = 0.9.

### Not done yet

- No TEST runs (LEFT button) were run before the USB cable disconnected.
- I didn't record whether holding LEFT moves the arm physically to the left
  (README checklist item 3).
- I haven't tried rearranging the bricks to see it re-learn.

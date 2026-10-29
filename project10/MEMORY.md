# Project 10 Haunted House: session memory / handoff

Last updated: 2026-10-28. Read this first, then `SPEC.md` (requirements, timeline,
message contract, test results) and `README.md` (how to set up and run the hubs).
The repo rules in `../AGENTS.md` apply: student portfolio, never invent work or
results, and no git actions unless the student asks.

## Pickup prompt (paste into a new Claude session)

> I'm continuing Project 10: Haunted House in my portfolio repo. Read
> `project10/MEMORY.md`, then `project10/SPEC.md` and `project10/README.md`.
> Three SPIKE Prime hubs run the show with spikecomm Beacon mode, and it works.
> The pull-up was just changed to 6.7 s and still needs a test. Check with me
> where things stand before changing code, and help me with the next step: [describe].

## Where things stand

- **Working on the real hubs:** the link test, then the full show from the Hub C
  LEFT test button (all motor directions correct) and from a real azure ball on
  both eyes (sensors D and B, several shows in a row). The skull re-arms after each show.
  At the end of the last session, Hub B logged `Not hearing ['A']` during show 5.
  Hub A was probably switched off or carried away, but this hasn't been checked.
- **Being tuned:** the top pull-up time (`PULL_MS` in `hub_a_dropper.py`).
  History: 3 s at 500°/s was too short. 10 s at 800°/s was too long (7488°
  measured). 6 s gave 4636° ("better"), 6.5 s gave 5036° ("a bit better").
  **6.7 s is loaded on Hub A.** One show ran at 6.7 s and measured 5135°, but the
  student hasn't said yet whether that's the right length. Release is max speed
  (1050°/s) back to the pre-pull position.
- **Not tested yet:** AC-4 (hits during a show ignored) and AC-5 (Hub A off, 60 s re-arm). See SPEC.md.
- **Not done:** the `project10.html` portfolio page and home card. Nothing is
  committed: `project10/` and several `IMG_*` files in the repo root are untracked.

## Hardware and tool facts (learned the hard way)

| Hub | Part | USB port (the name comes from the hub's serial) |
|---|---|---|
| A | Dropper | `/dev/cu.usbmodem203D306F52301` |
| B | Skull | `/dev/cu.usbmodem3367395933381` |
| C | Slide | `/dev/cu.usbmodem365B377C32381` |

- `mpremote` 1.29 is installed in the conda Python (`pip3 install mpremote`).
  `mpremote connect list | grep LEGO` shows which hubs are plugged in.
- A hub only shows up on USB when it is **switched on** and the cable carries
  data. This came up several times: ask the student to turn the hub on or reseat the cable.
- Start or restart a program with `mpremote connect <port> soft-reset run <file>`,
  run in the background. Stop any old `mpremote` process on that port first
  (`pkill -f "mpremote connect <port>"`). Unplugging ends mpremote with
  `OSError: [Errno 6] Device not configured`. That's harmless, and the program keeps running.
- spikecomm programs **must** start from the REPL or mpremote, never the SPIKE App's Run button.
- Firmware checks: `color.AZURE == 4`, `motor.HOLD == 2`, and
  `motor.run_to_relative_position` exists. Hubs need about 3–8 s after starting before they print `Hearing [...]`.
- When reading background output files, cat the specific task file. Don't use
  `ls -t | head -1 | xargs cat`: it once picked its own output file and hung.
- Student's workflow: one hub at a time on one cable. Hub B (and A) can stay
  plugged in during tests so their logs show `Show N started: …`, `Unwind N degrees`, and so on.

## Student decisions not obvious from the code

- The hub letters were renamed partway through: **A = Dropper, B = Skull, C = Slide**.
- One azure reading counts as a hit. The ball bounces off, so there's no debounce and no "ball must leave" re-arm.
- The test trigger is LEFT on **Hub C**, not Hub B.
- The candy pusher always starts anticlockwise after a restart. The student resets it by hand.
- A runs the whole timeline on its own clock from a single trigger, chosen to keep Bluetooth messages to a minimum.
- The professor's guide is https://github.com/edanahy/spikecomm. `spikecomm.py` here is an unmodified copy of v1.2.0.

## Suggested skills

- `engineering-advanced-skills:spec-driven-workflow`: the student asked for it. Update `SPEC.md` before changing behavior.
- `mattpocock-skills:grilling`: the student asked for it when giving new instructions. Ask one decision at a time, each with a recommendation.
- `anthropic-skills:built-in-browser`: for previewing a `project10.html` portfolio page. Follow the auto-memory note `portfolio-browser-preview` and use a temporary `http.server`, not `file://`.

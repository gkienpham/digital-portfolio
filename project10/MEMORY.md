# Project 10 Haunted House: session memory / handoff

Last updated: 2026-10-30. Read this first, then `SPEC.md` (requirements, timeline,
message contract, acceptance-test results, edge cases) and `README.md` (how to set
up and run the hubs). The code is `hub_a_dropper.py`, `hub_b_skull.py` and
`hub_c_slide.py`. The repo rules in `../AGENTS.md` apply: this is a student
portfolio, so never invent work or results, and take no git actions unless the
student asks.

## Pickup prompt (paste into a new Claude session)

> I'm continuing Project 10: Haunted House in my portfolio repo
> (`~/Documents/digital-portfolio`). Read `project10/MEMORY.md` first, then
> `project10/SPEC.md` and `project10/README.md`. Three LEGO SPIKE Prime hubs
> (A = Dropper, B = Skull, C = Candy pusher) run the show over Bluetooth with
> spikecomm Beacon mode, and the full show works. I have one USB cable and plug
> in one hub at a time. Check with me where things stand before changing code,
> commit or push to GitHub only when I ask, and help me with the
> next step: [describe].

## Where things stand (2026-10-30)

- **Works on the real hubs:**
  - full shows from a real azure ball (both eyes, before the any-color change) and from LEFT on Hub C or Hub A
  - 29-turn pull at half speed (10,440° measured every time) and the matching unwind
  - the skull re-arming after each show
  - RIGHT on Hub A stopping the motors
  - RIGHT on Hub C pushing candy without a show
  - per-AC results are in `SPEC.md`
- **Loaded but not tested:**
  - LEFT on Hub A resetting the dropper after an emergency stop (AC-7)
  - a RIGHT press on Hub C *during* a show (AC-8)
  - AC-4: hits during a show are ignored
  - AC-5: with Hub A off, B re-arms after 90 s. This happened by accident, but wasn't run as a test.
- **Pull length:** **19.5 turns** (7,020°) since 2026-10-30, running on Hub A but not run
  in a show yet. Before that, 28.5 was loaded but never run; 26 ran one show
  (unwind 9,358°, then RIGHT during the unwind); 20 ran two full shows (unwind
  7,200° and 7,201°); 19 ran three shows; then 20 again (one show started, its
  end not seen in the log). During the 19-turn shows, RIGHT then LEFT
  on Hub A logged `Reset: unwinding 1398 degrees` / `Reset done`, then a
  normal show ran (AC-7 evidence; not recorded in `SPEC.md` until the student
  OKs it). Tuning history is in the timeline footnotes in `SPEC.md`:
  - 6.7 s
  - then 33.5 turns
  - then 29 turns
  - then speeds halved
  - then 28.5 turns, then 26 turns, then 20 turns, then 19 turns, then 20 again, then 19.5 turns
- **Any-color trigger** (`hub_b_skull.py`, `NOT_A_BALL` setting, SPEC
  FR-1/AC-3/EC-7) is running on Hub B since 2026-10-30. Both empty eyes read
  `color.UNKNOWN` (-1) 400 of 400 times, and B armed without a false show. Not
  yet tried with a ball.
- **Git:** local commits only.
  - `1c38d94`: first version
  - `f1d114b`: 2026-10-29
  - `3f659f6`: 29 turns, half speed, 90 s, emergency stop
  - `db883ef`: LEFT reset, 600°/s candy
  - a 2026-10-30 commit for the Hub C RIGHT candy button and this handoff (see `git log`)
  - Push only when the student asks (first push: 2026-10-30).
  - The `IMG_*`, `.mov` and PDF files in the repo root stay out of git (the student's choice).
- **Project finished (2026-10-30).** Final settings: 19.5-turn pull, any-color
  trigger. The portfolio page `../project10.html` and its home-page card are
  done. Images are `../images/project10*.jpg`: a hero cutout from IMG_7729 and a
  booth crop from IMG_7731 (no faces), plus cutouts from IMG_7733,
  `dropper.jpg` and `skull.jpg`. The page's code blocks are copies of the
  `hub_*.py` files, so if the code changes, update the page too.
- **YouTube video `JhY2_mKiFgQ`** was Private when the page was built. The
  student set it to Unlisted on 2026-10-30, so the embed plays.
- **Git:** pushed to `origin/main` (GitHub Pages) on 2026-10-30 at the
  student's request.

## Hardware and tool facts (learned the hard way)

| Hub | Part | USB port (named after the hub's serial) |
|---|---|---|
| A | Dropper | `/dev/cu.usbmodem203D306F52301` |
| B | Skull | `/dev/cu.usbmodem3367395933381` |
| C | Candy pusher (slide) | `/dev/cu.usbmodem365B377C32381` |

- `mpremote` 1.29 is in the conda Python. `mpremote connect list | grep LEGO`
  shows which hub is plugged in. A hub only shows up when it's switched on, and it
  can take a few seconds after plugging in, so retry the listing for up to 10 s.
- **Start a program:** `pkill -f "mpremote connect <port>"`, then
  `mpremote connect <port> soft-reset run <file>` in the background (from
  `project10/`). The hub prints `Hearing [...]` once it hears both other hubs,
  usually within 3–10 s.
- **Turning a hub on does NOT start its program.** After the student power-cycles
  hubs, each one has to be plugged in and started again. This came up many times.
- **Unplugging is fine.** mpremote exits with `OSError: [Errno 6] Device not
  configured`, but the program keeps running on battery.
- **The link screen needs both other hubs.** `Hearing`/`Not hearing` only prints
  when the ✓/✗ status changes. A hub that hears one other hub but not the second
  stays on `Not hearing [both]`. To see exactly who is broadcasting, run a
  one-shot scan from the plugged-in hub:
  `mpremote connect <port> exec "from spikecomm import Scanner; print(Scanner('!B').read(timeout=3000))"`.
  It returns `[state, count]` or `None`. This **stops that hub's program**, so
  restart it afterwards.
- **A hub started mid-show ignores that show.** The first count heard from a hub
  is only remembered, which is the protection against restarts. If the ball is
  hit while a hub is still starting, that hub sits the show out. The skull then
  waits for its 90 s timeout. This explained "the dropper isn't dropping".
- **Hub A treats its motor positions at program start as "home"** for the LEFT
  reset. Make sure the platforms are closed and the knife is resting on them
  before starting A.
- spikecomm programs must start from mpremote or the REPL, never the SPIKE App's
  Run button.
- Firmware has `color.AZURE == 4`, `motor.HOLD`, `motor.stop`,
  `motor.run_to_relative_position` and `button.RIGHT`/`button.LEFT`.
- When waiting on background output, cat the specific task file. Never use
  `ls -t | head -1`, which once picked its own output file and hung.

## Student decisions not obvious from the code

- The hub letters were renamed early on: **A = Dropper, B = Skull, C = Slide/candy pusher**.
- Any color reading (anything in `NOT_A_BALL` excluded, by default only `color.UNKNOWN`) counts as a hit; azure only until 2026-10-30. The ball bounces off, so there's no debounce.
- B is the only hub that starts shows. Test triggers ask B for a show:
  - LEFT on C raises C's count
  - LEFT on A sets A's state to 2
- **Hub A buttons:**
  - RIGHT is the emergency stop: all three motors stop and the screen shows ✗.
  - LEFT after a stop is "reset, then wait": the platforms close, the string
    unwinds to home, A reports ready and waits. The student chose this over
    "end the program" and over "resume the show".
- **Hub C buttons:**
  - RIGHT pushes one candy any time and does nothing else.
  - LEFT starts a test show.
  - Once a hub-LEFT press was taken for the student's "right", so if button
    confusion comes up, ask whether the hub is mounted rotated.
- Candy push: 360° anticlockwise at 600°/s, ending at its start. Pushes add up from
  a target position, so overlapping presses still end at the start.
- The dropper runs its whole timeline on its own clock from one trigger, to keep
  Bluetooth messages to a minimum.
- Professor's guide: https://github.com/edanahy/spikecomm. `spikecomm.py` is an
  unmodified copy of v1.2.0.

## Suggested skills

- `engineering-advanced-skills:spec-driven-workflow`: the student asked for it.
  Update `SPEC.md` (FRs, ACs, edge cases) before changing behavior.
- `mattpocock-skills:grilling`: when new instructions leave a real choice, ask
  one decision at a time, each with a recommendation.
- `anthropic-skills:built-in-browser`: for previewing a `project10.html`
  portfolio page. Use a temporary `http.server` (see the auto-memory note
  `portfolio-browser-preview`), not `file://`.

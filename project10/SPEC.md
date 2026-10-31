# Spec: Project 10 Haunted House — show programs

**Status:** Approved and implemented; pull 19.5 motor turns at half speed (20 and 19 turns ran in shows on the hubs; 19.5 not yet run) · **Date:** 2026-10-30
**Code:** `hub_a_dropper.py`, `hub_b_skull.py`, `hub_c_slide.py` in this folder, using spikecomm 1.2.0 (already on every hub).

## Context
A 3-hub link test proved that all three hubs hear each other in real time using Beacon mode (`!A`/`!B`/`!C`, message `state;count`, an event = the count going up). The show programs replaced the link test. Every decision below came from the student's instructions plus a grilling Q&A.

| Hub | Part | Ports |
|---|---|---|
| A | Dropper | **F** right platform (medium), **B** left platform (medium), **A** top pull-up (large) |
| B | Skull | **B** and **D** color sensors |
| C | Slide | **A** candy pusher |

## Show timeline (t = 0 when a ball is seen)
| t | Hub | Action |
|---|---|---|
| 0 | B | Either sensor reads **any color** (anything but `color.UNKNOWN`, the "nothing there" reading) **once** (no debounce, because the ball only flashes past). B's count +1, then B ignores the sensors until it re-arms |
| ~0.1 | C | Candy push: one full turn, 360° anticlockwise at 600°/s, ending where it started (changed from alternating 180° on 2026-10-29; 300°/s until 2026-10-30) |
| 5 | A | Drop: F **+90° clockwise** and B **−90° anticlockwise**, both started at the same moment, 800°/s |
| 10 | A | Pull-up: port A clockwise **19.5 motor turns (7,020°) at 400°/s**, about 18 s, ending in **hold** so the knife stays up (6.7 s until 2026-10-29, then 33.5 turns, then 29 turns, then 28.5 turns (never run), then 26 turns, then 20 turns, then 19 turns, then 20 turns until 2026-10-30; 800°/s until 2026-10-30) |
| ~28.1 | A | Wait 2 s |
| ~30.1 | A | Platforms back: F −90°, B +90°, at the same moment, 300°/s (0.7 s allowed) |
| ~30.8 | A | Release: port A back to the position from before the pull, at **525°/s** (half the max; 1050°/s until 2026-10-30), about 13 s, so it unwinds exactly what was pulled |
| ~45 | A | A's count +1 = "ready". B re-arms |

## Functional requirements
- FR-1 B MUST check both color sensors in a fast loop (about every 5 ms) and trigger on a single reading of any color from either one: anything not listed in the `NOT_A_BALL` setting (only `color.UNKNOWN`, "nothing there"). Changed from azure only on 2026-10-30.
- FR-2 B MUST ignore ball hits and test triggers while a show is running, and MUST re-arm when A's count goes up **or** 90 s after the trigger, whichever comes first.
- FR-3 C MUST push candy when B's count goes up: 360° anticlockwise, ending back at its start position.
- FR-4 A MUST run the timeline above on its own clock when B's count goes up, then increase its own count.
- FR-5 The two platform motors MUST be started back-to-back in the same step for the drop and for the return, so they move as a pair.
- FR-6 Pressing LEFT on **Hub C** MUST start a show exactly like a ball hit. C's count +1, and B treats it as a trigger, so B stays the only hub that decides when a show starts. LEFT does nothing on B.
- FR-9 Pressing LEFT on **Hub A** MUST start a full show exactly like FR-6: A's state becomes 2 ("test requested"), and an armed B treats that as a trigger. A then runs its timeline when B's count goes up, as usual. Added 2026-10-29.
- FR-10 Pressing RIGHT on **Hub A** at any time MUST stop all three dropper motors right away and leave the show (emergency stop). A then waits, motors stopped, until LEFT is pressed. B and C keep running (B re-arms after its 90 s timeout). Added 2026-10-30.
- FR-11 After an emergency stop, pressing LEFT on **Hub A** MUST reset the dropper: both platforms go back to where they were when A's program started (closed), then the pull-up motor unwinds back to its start position. A's count then goes up ("ready") and A waits for the next show. That LEFT press MUST NOT also start a test show. RIGHT during the reset stops it again. Added 2026-10-30 (replaces "the stop ends the program").
- FR-12 Pressing RIGHT on **Hub C** at any time MUST push one candy (360° anticlockwise) without starting a show. A press during a push adds one more full turn, so the pusher always ends at its start position. Added 2026-10-30.
- FR-7 Every hub keeps the link screen: ✓ when it hears both other hubs, ✗ otherwise. It prints each step to the console.
- FR-8 Every speed, time, angle and port MUST be a named setting at the top of its program (the student tunes them while testing).

## Non-functional requirements
- NFR-1 Candy starts within 0.5 s of the hit (one beacon hop).
- NFR-2 Beginner-readable code using only spikecomm and the SPIKE App 3 API, with no blocking calls inside callbacks. Motor moves are timed with `time.sleep_ms` in the main loop (callbacks still fire during sleep).

## Acceptance criteria (checked on the real hubs)
| AC | Criterion | Result |
|---|---|---|
| AC-1 | LEFT on Hub C: candy pushes right away, then drop (~5 s), pull-up (~10 s), close, release. Platforms move together | ✅ passed (all motor directions right) |
| AC-2 | A second show pushes candy the same full turn and the pusher ends at its start | ⬜ not tested since the 360° change (the old alternating 180° passed) |
| AC-3 | A thrown ball of any color hitting either eye starts a show, and an empty eye never does | ⬜ any-color version not tested (the azure-only version passed on both eyes, sensors D and B) |
| AC-4 | Hits during a show do nothing. After A's "ready", the next hit starts a new show | ⚠️ re-arm seen in the logs; hits *during* a show not tested on purpose |
| AC-6 | RIGHT on Hub A during a show stops the dropper motors (FR-10) | ✅ motors stopped when pressed during the pull (2026-10-30, while the stop still ended the program) |
| AC-8 | RIGHT on Hub C pushes one candy without a show, including during a show (FR-12) | ✅ RIGHT presses logged `Candy button: push` with no show request (2026-10-30); a press *during* a show not checked |
| AC-7 | After a stop, LEFT on Hub A closes the platforms, unwinds the string to its start, and the next ball runs a normal show (FR-11) | ⬜ not tested |
| AC-5 | With A switched off, a hit still pushes candy, B shows ✗, and B re-arms after 90 s | ⬜ not tested |

## Edge cases
- EC-1 A restarted mid-show: its count goes back to 0, which doesn't count as "ready". B's 90 s timeout re-arms it (raised from 60 s on 2026-10-30, when the show grew to about 60 s).
- EC-2 A program is started while the motors aren't in their start positions. The student sets them first: platforms closed, knife resting on them with slack, pusher at its start (README).
- EC-3 A motor turns the wrong way (SPIKE's "clockwise" is seen looking at the motor's face). Fix: flip the sign of that setting.
- EC-5 Emergency stop after the drop but before the pull: the knife hangs below the platforms, so the reset closes the platforms under nothing. The student lifts the knife back on top by hand.
- EC-6 A's program is started while the knife is pulled up or the platforms are open: A takes those positions as "home", so a later reset goes back to the wrong place. Same fix as EC-2: set everything up before starting A.
- EC-7 An empty eye reads a color instead of `color.UNKNOWN` (something close to the sensor, or bright light). B would start a show as soon as it re-arms, again and again. Fix: add that color to `NOT_A_BALL` in `hub_b_skull.py` (for example `color.BLACK`). Added 2026-10-30 with the any-color trigger.
- EC-4 B starts before A or C: the trigger still counts, and B's timeout covers a missing A.

## Message contract
| Prefix | `state` | `count` goes up when… | Who reacts |
|---|---|---|---|
| `!B` | 0 armed, 1 show running | a show starts (a ball or a test trigger) | A runs the timeline, C pushes candy |
| `!A` | 0 idle, 1 running timeline, 2 LEFT pressed (test request) | the timeline is finished ("ready") | B re-arms; state 2 makes an armed B start a show |
| `!C` | 0 | LEFT is pressed (test trigger) | B starts a show if armed |

The first count heard from a hub is only remembered and never acted on, so restarting a hub can't set anything off.

## Out of scope
- OS-1 Saving the pusher direction across restarts (not needed since the full-turn push, 2026-10-29).
- OS-2 Sounds and light effects beyond the ✓/✗ screen.
- OS-3 Git push (never; local commits only, when the student asks). The `project10.html` portfolio page was done separately on 2026-10-30.

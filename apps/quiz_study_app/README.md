# Quiz Study App

Lab 2 (INFO 5356), Section 3 — custom app running on the physical Reachy Mini.

This is a short quiz the robot runs with a participant, to see how they react to two different feedback styles: verbal-only vs. verbal plus a head gesture. It's built on two existing pieces rather than from scratch: the Reachy Mini SDK's audio playback (and, in the demo variant, its mic input), and the `yeah_nod` / `side_to_side_sway` moves from [pollen-robotics/reachy_mini_dances_library](https://github.com/pollen-robotics/reachy_mini_dances_library) (vendored in at the repo root, so a plain clone has everything it needs — no submodule setup).

## The gist

Each participant does two sessions of 5 questions, using two different quiz sets so nobody sees the same question twice. Which condition applies to which session depends on the sequence you pass in:

- **Condition A** — feedback audio only, no visible movement.
- **Condition B** — same audio, plus the head nods (correct) or shakes side to side (incorrect).

| sequence | session 1 | session 2 |
|---|---|---|
| AB | A | B |
| BA | B | A |
| AA | A | A |
| BB | B | B |

The robot asks each question out loud, the participant answers out loud, and whoever's running the session hears the answer and judges it themselves (correct/incorrect/repeat/interrupted/failed) — this is the actual study app, and it's what collected P01–P04's data. We went this route after testing automatic speech recognition (see `demo_stt_interaction.py` below) and finding transcription wasn't reliable enough on real speech to trust for real trial judgments — easier and more defensible to have a human judge it and log that.

## Integration map

- **Source apps/components combined:** (1) the Reachy Mini SDK's app-template structure and built-in audio pipeline (`mini.media.push_audio_sample` for output; `mini.media.start_recording()`/`get_audio_sample()` for input, used in the STT demo), and (2) `reachy_mini_dances_library`'s pre-built `yeah_nod` and `side_to_side_sway` moves for the non-verbal feedback gesture.
- **Reused as-is:** the dance library's move functions and their underlying rhythmic-motion engine — called directly via `AVAILABLE_MOVES`, not reimplemented.
- **Modified/new:** the quiz-trial orchestration layer (asking questions, judging answers, choosing which move and amplitude to play) didn't exist in either source project. The one new integration point connecting the two pieces is an `amplitude` parameter threaded into the dance library's move calls, so the exact same move plays at zero visibility (Condition A) or full visibility (Condition B) without changing its timing.
- **Interaction goal:** let a participant experience a short verbal quiz with Reachy Mini acting as a quiz-giving tutor, manipulating exactly one factor — whether feedback also includes a visible gesture — to see whether that changes perceived sociability/animacy (HRIES) and engagement.
- **Final-project connection:** this is a working prototype of "Reachy Mini as a learning tutor." A natural final-project direction extends this toward richer tutoring content, adaptive difficulty, or combining it with real-time speech recognition (prototyped separately below) once that's reliable enough for real judgments rather than just a demo.

## Files

```
apps/quiz_study_app/
├── main.py                     the real study app -- one run per participant, facilitator-judged
├── demo_conditions.py          scripted demo: one A cycle then one B cycle, no live input
├── demo_condition_a.py         standalone, logged demo: one Condition-A trial only
├── demo_condition_b.py         standalone, logged demo: one Condition-B trial only
├── demo_stt_interaction.py     live demo: real mic input + automatic judging, one cycle per condition
├── stt_utils.py                 speech-to-text helpers (faster-whisper) used by the STT demo only
├── test_recording.py            standalone sanity check for the mic/STT pipeline
├── quiz_content.py              the two question sets + feedback scripts
├── generate_audio.py            one-time: generates all 21 clips with macOS `say`, no API needed
├── audio/                        generated .wav files live here
└── logs/                         trial_log_<participant>.csv per participant session (main.py) +
                                    demo_trial_log.csv (demo_condition_a.py / demo_condition_b.py)

reachy_mini_dances_library/   vendored dependency, see above
```

## Setting it up

This assumes `reachy_mini` itself (the SDK) is already installed per the course's Reachy Mini setup guide (Canvas → Home → Course Logistics) -- that part isn't specific to this repo. What *is* specific to this repo:

```
git clone https://github.com/xinxuan-xs444/info5356-lab-2.git
cd info5356-lab-2
python3 -m venv reachy_mini_env
source reachy_mini_env/bin/activate
pip install -e ./reachy_mini_dances_library
pip install numpy soundfile scipy sounddevice faster-whisper
```

The `pip install -e ./reachy_mini_dances_library` step is required -- it's a vendored dependency in this repo (not on PyPI), and every app here imports from it (`AVAILABLE_MOVES`).

Then generate the audio clips once (offline, no API key):

```
cd apps/quiz_study_app
python generate_audio.py
```

That should produce 21 `.wav` files in `audio/` — 1 shared correct-feedback clip plus 5 questions and 5 incorrect-feedback clips per quiz set.

For the robot itself: on the physical robot, you don't start a daemon yourself — just make sure it's powered on and shows as connected in the Reachy Mini Control app, not stuck on "Standby."

## Running a real session

```
python main.py --participant P01 --sequence AB
```

`--sequence` is required (AB/BA/AA/BB). It runs a pre-flight check first that catches missing clips or dependencies before anyone's sitting in front of the robot waiting. Audio plays through the robot's own speaker (`request_media_backend = "webrtc"`) rather than your laptop.

Our actual 4 participants:

| participant | command |
|---|---|
| P01 | `--sequence AB` |
| P02 | `--sequence BA` |
| P03 | `--sequence AB` |
| P04 | `--sequence BA` |

As facilitator, for each question you'll see:

```
Judge the participant's answer yourself: [c]orrect / [i]ncorrect / [r]epeat / interru[x]ted / [f]ailed >
```

Typing a stray key just reprompts you, it won't make the robot re-ask the question — only `r` does that.

A CSV gets written automatically to `logs/trial_log_<participant>_<timestamp>.csv`, columns: `participant_id`, `session`, `condition`, `question_id`, `trial_outcome`, `correct`, `repeats`, `note`, `timestamp`.

## Demo scripts

```
python demo_conditions.py
```
Runs one A cycle and one B cycle back to back using the real app's own methods, with a scripted "correct" answer — no live input needed. This is what we used to capture clean condition-contrast footage for the report, since it doesn't depend on speech being heard correctly.

```
python demo_condition_a.py
python demo_condition_b.py
```
Each runs exactly one logged trial for its own condition only (Condition A / Condition B), reusing the same playback and gesture methods as the apps above. Unlike `demo_conditions.py`, these two append a row to `logs/demo_trial_log.csv` for every run -- condition, parameter value (gesture amplitude), start time, end time, completion status, and any error -- and explicitly confirm the trial starts and ends in the same neutral pose. This is what satisfies Section 3.3's testing/logging/reproducibility requirement specifically; `demo_conditions.py` is the demonstration clip, these two are the reproducible, logged test runs (tested in the MuJoCo simulator first, then on the physical robot).

```
python demo_stt_interaction.py
```
Runs one question under Condition A and one under Condition B, but this time the robot actually listens to and transcribes your spoken answer (locally, offline, via `faster-whisper`) and judges it automatically — no facilitator input at all. This demonstrates the speech-recognition capability working end-to-end, separate from the data that's actually reported: STT accuracy wasn't reliable enough on real speech to trust for real trial judgments, so it stays a demo rather than the study's data-collection method.

## A few things worth knowing

The gesture always runs in both conditions — what changes is the amplitude (0 for A, full for B), not whether it happens at all. That keeps the timing identical between conditions so A and B only differ in what's visible, not how long feedback takes. Which move plays depends on whether the answer was right or wrong, independent of condition — nod for correct, sway for incorrect, either way.

Audio now plays from the robot's own speaker, via `media_backend="webrtc"`. WebRTC negotiates its audio connection asynchronously in the background, so both `main.py` and the demo scripts pause for 2 seconds after connecting before pushing the first clip — without that pause, the very first clip can get silently dropped because the pipeline isn't ready yet (this happened on a real test run).

## Limitations to mention in the writeup

Facilitator judges answers manually in the real study, so it's not a blind measure — worth naming directly. Automatic speech recognition was prototyped (`demo_stt_interaction.py`) but found unreliable enough on real speech that it wasn't trusted for real trial data — a legitimate limitation and a concrete direction for a follow-up study once STT accuracy is improved. And obviously, 4 participants is a small sample for a class exercise — treat the results as exploratory rather than something to draw strong conclusions from.

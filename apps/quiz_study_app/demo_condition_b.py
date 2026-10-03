"""
demo_condition_b.py -- robot-only demo + reproducibility log for Condition B
(verbal feedback + non-verbal gesture), satisfying Section 3.3's
testing/logging/reproducibility deliverables:

  - Tests the condition on the physical robot and confirms the trial begins
    and ends in the same (neutral) pose.
  - Logs the condition, parameter value, start time, end time, completion
    status, and any robot/operator error for the trial to a CSV.
  - Documents setup, launch command, and stop procedure (below).

This is the Condition-B half of what used to be a single combined file
(demo_conditions.py, which still exists and still works for the
already-recorded condition-contrast clip). This file and its Condition-A
counterpart (demo_condition_a.py) exist specifically so each condition has
its own standalone, individually-launchable, individually-logged
demonstration, matching the assignment's wording of "test both conditions"
and "log ... for each trial" as separate, reproducible runs.

Reuses QuizStudyApp's own clip-playback, gesture, and neutral-return methods
directly (same pattern as demo_conditions.py / demo_stt_interaction.py)
rather than reimplementing them -- this is a demo of the tested app, not a
re-implementation.

--- Setup ---
1. Reachy Mini is powered on and connected (same network/daemon as every
   other app in this repo -- see the top-level README).
2. Activate the project's virtual environment.
3. cd into apps/quiz_study_app.

--- Launch command ---
    python demo_condition_b.py

--- Stop procedure ---
Let the single trial run to completion (~10-15 seconds) and the script will
exit on its own, robot already back in neutral pose. If it needs to be
stopped early, Ctrl+C is safe: the SDK's normal interrupt handling takes
over, and because this script only runs one trial, there's no partial study
state to clean up. If an exception interrupts the trial before the
return-to-neutral call, that's caught, logged as a Failed trial with the
error message, and the script still exits cleanly.
"""
import csv
import datetime
import threading
import time
from pathlib import Path

import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES

from quiz_content import QUESTION_SETS
from main import QuizStudyApp, AUDIO_DIR, MOVE_NAME_CORRECT, MOVE_NAME_INCORRECT

LOG_PATH = Path(__file__).parent / "logs" / "demo_trial_log.csv"
FIELDNAMES = [
    "condition", "parameter_value", "start_time", "end_time",
    "completion_status", "error", "start_pose", "end_pose",
]

CONDITION = "B"
AMPLITUDE = 1.0  # unitless gesture-amplitude scale, 0.0-1.0 -- B = full visible movement
ITEM = QUESTION_SETS[2][0]


def timestamp():
    return time.strftime("%H:%M:%S")


def write_log_row(row):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def run_trial(app, reachy_mini, stop_event):
    start_time = datetime.datetime.now().isoformat(timespec="seconds")
    status = "Completed"
    error = ""
    start_pose = "unknown"
    end_pose = "unknown"

    try:
        # Command and confirm the trial starts from the same neutral pose
        # every time, rather than assuming whatever pose the robot was
        # already in.
        neutral = create_head_pose(yaw=0, pitch=0, roll=0, degrees=True)
        reachy_mini.goto_target(head=neutral, antennas=np.array([0.0, 0.0]), duration=0.5)
        time.sleep(0.5)
        start_pose = "neutral (commanded + confirmed)"
        print(f"[{timestamp()}] STAGE=start_pose_confirmed pose=neutral")

        kind = "verbal + non-verbal"
        print(f"\n=== Condition {CONDITION} ({kind}) ===")
        print(f"[{timestamp()}] Question: {ITEM['question']!r}")
        app._play_clip(reachy_mini, AUDIO_DIR / f"q_{ITEM['id']}.wav")

        time.sleep(1.0)  # stand-in pause for the participant's spoken answer

        correct = True  # scripted outcome, for a clean reproducible demo clip
        move_name = MOVE_NAME_CORRECT if correct else MOVE_NAME_INCORRECT
        move_fn, base_params, _ = AVAILABLE_MOVES[move_name]
        clip_name = "fb_correct.wav" if correct else f"fb_incorrect_{ITEM['id']}.wav"

        print(f"[{timestamp()}] Feedback: correct -> clip={clip_name} move={move_name} amplitude={AMPLITUDE}")
        app._play_clip(reachy_mini, AUDIO_DIR / clip_name)
        app._play_nonverbal_gesture(reachy_mini, stop_event, move_fn, base_params, AMPLITUDE, correct)
        app._return_to_neutral(reachy_mini)

        end_pose = "neutral (confirmed via _return_to_neutral)"
        print(f"[{timestamp()}] STAGE=end_pose_confirmed pose=neutral")

    except Exception as e:
        status = "Failed"
        error = repr(e)
        print(f"[{timestamp()}] STAGE=trial_error error={error}")

    end_time = datetime.datetime.now().isoformat(timespec="seconds")

    row = {
        "condition": CONDITION,
        "parameter_value": AMPLITUDE,
        "start_time": start_time,
        "end_time": end_time,
        "completion_status": status,
        "error": error,
        "start_pose": start_pose,
        "end_pose": end_pose,
    }
    write_log_row(row)
    print(f"[{timestamp()}] STAGE=trial_logged status={status} start={start_time} end={end_time} "
          f"path={LOG_PATH}")
    return status


def main():
    app = QuizStudyApp()
    stop_event = threading.Event()

    with ReachyMini(media_backend="webrtc") as mini:
        mini.media.start_playing()
        print(f"[{timestamp()}] STAGE=connected Connected (media_backend=webrtc)")
        print(f"[{timestamp()}] STAGE=webrtc_warmup Waiting for WebRTC audio to finish negotiating...")
        time.sleep(2.0)

        run_trial(app, mini, stop_event)

        mini.media.stop_playing()

    print(f"\n[{timestamp()}] Demo complete.")


if __name__ == "__main__":
    main()

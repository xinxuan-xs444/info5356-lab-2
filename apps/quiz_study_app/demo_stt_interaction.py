"""
demo_stt_interaction.py -- standalone demo of real speech-to-text
interaction with Reachy Mini, run once under each condition: the robot
asks a question through its own speaker, actually listens to and
transcribes the spoken answer through its own microphone, judges it
automatically, and responds with audio (+ gesture, in Condition B)
accordingly.

This is a DEMONSTRATION of a capability, not the real user-study app.
The actual study (main.py, used for P01-P04 and any further participants)
stays on the original Wizard-of-Oz design -- facilitator judges the
spoken answer manually, no mic input captured -- because the STT here
was found to be unreliable enough on real speech that it isn't trustworthy
for real trial judgments (see the report's Section 7.3 "proposed
improvement" writeup). This file exists to show the capability working
end-to-end, across both conditions, separate from the data that actually
gets reported.

Reuses QuizStudyApp's own clip-playback and gesture methods directly
(same pattern as demo_conditions.py) rather than reimplementing them, and
reuses the record_answer()/transcribe()/is_correct() pipeline from
stt_utils.py, which wraps the real reachy_mini.media audio-input API
(start_recording()/get_audio_sample()/stop_recording()) confirmed by
introspecting the installed SDK directly.

Usage:
    cd apps/quiz_study_app
    python demo_stt_interaction.py
"""
import threading
import time

from reachy_mini import ReachyMini
from reachy_mini_dances_library.collection.dance import AVAILABLE_MOVES

from quiz_content import QUESTION_SETS
from main import QuizStudyApp, AUDIO_DIR, MOVE_NAME_CORRECT, MOVE_NAME_INCORRECT
from stt_utils import record_answer, transcribe, is_correct

RECORD_SECONDS = 4.0


def timestamp():
    return time.strftime("%H:%M:%S")


def run_one_question(app, reachy_mini, stop_event, label, amplitude, item):
    kind = "verbal only" if amplitude == 0.0 else "verbal + non-verbal"
    print(f"\n=== Condition {label} ({kind}) ===")
    print(f"Question: {item['question']!r}")
    app._play_clip(reachy_mini, AUDIO_DIR / f"q_{item['id']}.wav")

    print(f"[{timestamp()}] STAGE=recording_start Listening for {RECORD_SECONDS}s -- answer out loud now")
    audio = record_answer(reachy_mini, duration_s=RECORD_SECONDS)
    transcript = transcribe(audio)
    print(f"[{timestamp()}] STAGE=transcribed transcript={transcript!r}")

    if not transcript:
        print(f"[{timestamp()}] STAGE=no_speech_detected (demo only -- no auto-repeat here)")
        return

    correct = is_correct(transcript, item["answer"])
    move_name = MOVE_NAME_CORRECT if correct else MOVE_NAME_INCORRECT
    move_fn, base_params, _ = AVAILABLE_MOVES[move_name]
    clip_name = "fb_correct.wav" if correct else f"fb_incorrect_{item['id']}.wav"

    print(f"[{timestamp()}] STAGE=feedback outcome={'correct' if correct else 'incorrect'} "
          f"clip={clip_name} move={move_name} amplitude={amplitude}")
    app._play_clip(reachy_mini, AUDIO_DIR / clip_name)
    # Gesture always runs (same timing both conditions); amplitude=0.0 in
    # Condition A means the offsets scale to zero -- no visible movement --
    # while amplitude=1.0 in Condition B shows the full nod/sway. Same
    # logic as main.py and demo_conditions.py, just driven by a real
    # transcribed answer instead of a scripted one here.
    app._play_nonverbal_gesture(reachy_mini, stop_event, move_fn, base_params, amplitude, correct)
    app._return_to_neutral(reachy_mini)


def main():
    app = QuizStudyApp()
    stop_event = threading.Event()

    item_a = QUESTION_SETS[1][0]
    item_b = QUESTION_SETS[2][0]

    # webrtc: routes audio through the robot's own speaker and mic,
    # same backend main.py now uses for its one audio-output change.
    with ReachyMini(media_backend="webrtc") as mini:
        mini.media.start_playing()

        print(f"[{timestamp()}] STAGE=connected Connected (media_backend=webrtc)")
        print(f"[{timestamp()}] STAGE=webrtc_warmup Waiting for WebRTC audio to finish negotiating...")
        time.sleep(2.0)

        run_one_question(app, mini, stop_event, "A", amplitude=0.0, item=item_a)
        time.sleep(1.5)
        run_one_question(app, mini, stop_event, "B", amplitude=1.0, item=item_b)

        mini.media.stop_playing()

    print(f"\n[{timestamp()}] Demo complete.")


if __name__ == "__main__":
    main()

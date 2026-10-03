"""
hello_world.py -- Lab 2, Section 2.

Starting point: the antenna-movement template given in the assignment,
stored here unmodified.

Modification (the one required change): after the antenna sequence, the
robot enables its built-in daemon-side camera face tracking
(start_head_tracking) so the head orientation is driven by whatever the
camera actually sees, instead of a scripted pose. This is the
camera-based-input option named in the assignment ("move based on sensor
detection of hands, faces etc"), using the real SDK method confirmed by
introspecting the installed reachy_mini package (ReachyMini.start_head_tracking,
.get_tracked_face, .stop_head_tracking) -- not a hand-rolled vision pipeline.

Expected outcome: antennas sweep out (0.3, -0.3), sweep the other way
(-0.3, 0.3), then return to neutral (0.0, 0.0) -- exactly as in the
original template. Then head tracking turns on; if a face is in the
camera's view, get_tracked_face() should report it, and the head should
visibly turn to follow a person moving in front of the robot during the
5-second tracking window. Tracking then turns off and the head returns
to neutral.

Actual outcome: fill in after running on the physical robot -- note
whether a face was detected, how the head tracking looked (smooth vs.
laggy, any false starts), and what happened if no face was in view.

Usage:
    python hello_world.py
"""
import time

from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose


def timestamp():
    return time.strftime("%H:%M:%S")


with ReachyMini() as mini:
    mini.enable_motors()

    print(f"[{timestamp()}] STAGE=connected Connected, moving antennas...")

    mini.goto_target(
        antennas=[0.3, -0.3],
        duration=1.0
    )

    mini.goto_target(
        antennas=[-0.3, 0.3],
        duration=1.0
    )

    mini.goto_target(
        antennas=[0.0, 0.0],
        duration=1.0
    )

    print(f"[{timestamp()}] STAGE=antennas_done Done with antennas")

    # --- the one required change starts here: camera-based head tracking ---
    print(f"[{timestamp()}] STAGE=face_tracking_start Enabling camera-based head "
          f"tracking -- move in front of the robot now")
    mini.start_head_tracking(weight=1.0)

    try:
        face = mini.get_tracked_face(wait=True, timeout=5.0)
        print(f"[{timestamp()}] STAGE=face_detected face={face}")
    except Exception as e:
        print(f"[{timestamp()}] STAGE=face_not_detected error={e!r}")

    print(f"[{timestamp()}] STAGE=tracking_window Holding tracking active for "
          f"5s -- move side to side to see the head follow")
    time.sleep(5.0)

    print(f"[{timestamp()}] STAGE=face_tracking_stop Disabling head tracking")
    mini.stop_head_tracking()

    neutral = create_head_pose(yaw=0, pitch=0, roll=0, degrees=True)
    mini.goto_target(head=neutral, duration=1.0)

    print(f"[{timestamp()}] STAGE=done Done")

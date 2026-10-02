"""
hello_world.py -- Lab 2, Section 2.

Starting point: the antenna-movement template given in the assignment.
Modification (the one required change): each antenna movement now also
carries a HEAD movement, so the robot nods forward/back in sync with the
antennas instead of moving only the antennas. This uses create_head_pose +
goto_target(head=..., antennas=...), the same pattern already verified
working on the physical robot in apps/quiz_study_app/main.py.

Expected outcome: antennas sweep out (0.3, -0.3), sweep the other way
(-0.3, 0.3), then return to neutral (0.0, 0.0) -- exactly as in the
original template -- while the head simultaneously tilts down, then up,
then back to neutral, finishing in the same resting pose it started in.

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

    print(f"[{timestamp()}] STAGE=connected Connected, moving antennas and head...")

    head_down = create_head_pose(yaw=0, pitch=15, roll=0, degrees=True)
    head_up = create_head_pose(yaw=0, pitch=-15, roll=0, degrees=True)
    head_neutral = create_head_pose(yaw=0, pitch=0, roll=0, degrees=True)

    print(f"[{timestamp()}] STAGE=move_1 target=antennas[0.3,-0.3]+head_down")
    mini.goto_target(
        head=head_down,
        antennas=[0.3, -0.3],
        duration=1.0,
    )

    print(f"[{timestamp()}] STAGE=move_2 target=antennas[-0.3,0.3]+head_up")
    mini.goto_target(
        head=head_up,
        antennas=[-0.3, 0.3],
        duration=1.0,
    )

    print(f"[{timestamp()}] STAGE=neutral_recovery target=antennas[0.0,0.0]+head_neutral")
    mini.goto_target(
        head=head_neutral,
        antennas=[0.0, 0.0],
        duration=1.0,
    )

    print(f"[{timestamp()}] STAGE=done Done")

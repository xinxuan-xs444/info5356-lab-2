# INFO 5356 — Lab 2: HRI Research Methods

Xinxuan Shen (xs444) · Vishnupriya Rayaprolu (vr362)

This repo is the full submission for Lab 2: a small controlled pilot study on the physical Reachy Mini, comparing verbal-only feedback (Condition A) against verbal + non-verbal gesture feedback (Condition B) in a short quiz-tutor interaction. The written report (problem statement, study design, results, discussion) was submitted separately as a PDF on Gradescope; this repo is the reproducible side of the submission — the application code, study materials, raw and analysis-ready data, logs, figures, and video demonstrations the report is based on.

## Repo layout, mapped to the assignment sections

```
.
├── apps/
│   ├── hello_world/            Section 2 — hello_world.py
│   └── quiz_study_app/         Section 3 — the custom app (see its own README for full detail)
├── reachy_mini_dances_library/ Vendored dependency (its own README is inside this folder)
├── Video records/              Clips for Sections 1-3
├── Study materials/            Section 5 — HRIES questionnaires (Conditions A & B)
├── User study data/            Sections 5-6 — raw survey responses + the analysis-ready dataset
├── Related work/               Section 4 — the two cited papers (Ho 2026; Leusmann et al. 2025)
└── README.md                   this file
```

### Section 1 — Teleoperation
No custom code for this one — we used the built-in Reachy Mini Telepresence app (via the Reachy Mini Control App), not a script of our own. The evidence is in `Video records/`: `1.3 teleoperation.mp4`, `1.4 first run.mp4`, `1.4 final run.mp4`. Log excerpts and the sim-to-real comparison are in the submitted report.

### Section 2 — Hello World
`apps/hello_world/hello_world.py` — the provided antenna-movement template, modified to add camera-based head tracking (`start_head_tracking` / `get_tracked_face` / `stop_head_tracking`) after the antenna sequence. Run with:
```
python apps/hello_world/hello_world.py
```
Demo clip: `Video records/HelloWorlddemo.mp4`.

### Section 3 — Custom app (the quiz study)
Everything lives in `apps/quiz_study_app/` — the real study app (`main.py`), the Section-3 demonstration script (`demo_conditions.py`), the per-condition logged/reproducibility demos (`demo_condition_a.py` / `demo_condition_b.py`), the speech-recognition prototype (`demo_stt_interaction.py`), generated audio, and the trial logs. **See `apps/quiz_study_app/README.md` for the full integration map, setup, and run instructions** — that file has all the detail that would otherwise be duplicated here. Demo clip: `Video records/ApplicationDemo.mp4`.

### Sections 4-6 — Study design, materials, and data
- `Related work/` — the two papers our HRI problem statement is grounded in.
- `Study materials/` — the HRIES questionnaires (as administered) for both conditions.
- `User study data/` — the de-identified survey responses (`HRIES questionnaire for Condition A/B - responses.csv`) and the combined `analysis-ready dataset.xlsx`, which also has the data dictionary as its second sheet.
- `apps/quiz_study_app/logs/` — the raw per-trial CSVs the app itself generated: one per real participant (`trial_log_P01...csv` through `P04`), plus `demo_trial_log.csv` from the Section 3.3 demo scripts.

### Section 7 — Analysis
`apps/quiz_study_app/analysis/sociability_scores_by_condition.png` — the required participant-level paired figure (HRIES Sociability by condition, one line per participant). The dimension-score calculations themselves are shown worked out by hand in the submitted report; this repo doesn't yet have a standalone analysis script that reproduces them from the raw CSVs.

### Section 8 — This repo + README
You're reading it. The submitted report PDF is the primary writeup; this repo is the reproducibility companion referenced throughout it.

## Setup

This assumes `reachy_mini` itself (the SDK) is already installed per the course's Reachy Mini setup guide — that part isn't specific to this repo.

```
git clone https://github.com/xinxuan-xs444/info5356-lab-2.git
cd info5356-lab-2
python3 -m venv reachy_mini_env
source reachy_mini_env/bin/activate
pip install -e ./reachy_mini_dances_library
pip install numpy soundfile scipy sounddevice faster-whisper
```

`pip install -e ./reachy_mini_dances_library` is required — it's vendored in this repo (not on PyPI), and both apps import from it.

For Reachy Mini itself: power it on and confirm it shows connected in the Reachy Mini Control app before running anything — you don't start a daemon yourself.

## Running things

- Hello world: `python apps/hello_world/hello_world.py`
- Real quiz study session: see `apps/quiz_study_app/README.md` (`python main.py --participant <ID> --sequence <AB|BA|AA|BB>`, run from inside `apps/quiz_study_app/`)
- Demo scripts (condition contrast clip, per-condition logged runs, speech-recognition demo): also documented in `apps/quiz_study_app/README.md`

## Reproducing the analysis

The HRIES item-level responses are in `User study data/HRIES questionnaire for Condition A/B - responses.csv`; the dimension scores (sociability/animacy/disturbance/agency), manipulation check, objective measure, and qualitative responses are compiled in `User study data/analysis-ready dataset.xlsx`, with the scoring rule documented on its data-dictionary sheet. The paired figure for the primary outcome (sociability) is `apps/quiz_study_app/analysis/sociability_scores_by_condition.png`. Full results tables, the qualitative coding table, and the discussion are in the submitted report PDF.

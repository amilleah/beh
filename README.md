# Behavioral Experiment (Online + In‑Person)

This repository contains two matched implementations of a rapid sentence comparison task:

- `online/`: A PCIbex/PennController experiment for web deployment
- `in-person/`: A PsychoPy experiment for lab use

Both versions share the same stimulus schema and timing structure to enable dual use and comparable data.

## Structure

- online/
  - `data_includes/main.js`: Experiment flow and timings (PennController)
  - `chunk_includes/*.html`: Consent, welcome, instructions, begin, final screens
  - `chunk_includes/stimuli.csv`, `chunk_includes/practice.csv`: Stimulus lists (Match, Condition, Sentence, Probe)
- in-person/
  - `main.py`: PsychoPy experiment
  - `stimuli/stimuli.csv`, `stimuli/practice.csv`: Stimulus lists (the same as in online/)
  - `stimuli/feedback.csv`: Optional fun-fact/joke content for breaks
  - `port_open_send.py`: Trigger/port helper
  - `pyproject.toml`: Python project metadata
- logs/: Participant CSV output (created on run)

## Stimulus Schema

All CSVs use the same columns:
- `Match`: Match/Mismatch indicator (e.g., Match/Mismatch or 1/0)
- `Condition`: Numeric condition 1–4 (drives trigger mapping in-person)
- `Sentence`: Prime/first item
- `Probe`: Target/second item

## Task Flow

- Fixation (+) → blank → Sentence → blank → Probe → blank (response window) → jitter
- Keys: SAME = `2`, DIFFERENT = `1`
- Practice shows feedback (Correct/Wrong); main blocks do not

## Timings

- Fixation: 200 ms
- Blank1: 200 ms
- Sentence: 300 ms
- Blank2: 500 ms
- Probe: 300 ms
- Feedback (practice only): 500 ms
- Jitter: 300–700 ms in 10 ms steps

## Online (PCIbex/PennController)

- Entry: `online/data_includes/main.js`
- Assets: `online/chunk_includes/*.html`, `online/chunk_includes/*.csv`
- Configure your hosting (e.g., PCIbex Farm or self-hosted) and upload the entire `online/` folder contents.
- Prolific integration: `final` screen contains a completion link to update.

## In‑Person (PsychoPy)

### Requirements

- Requirements found in pyproject.toml (install via pip or uv)
- Serial port for sending event triggers (Optional, else warning)

### Run Options (GUI)

- Participant ID
- Fullscreen (on/off)
- Auto respond? (debug-only)
- Use frame-based timing? (on by default)
  - On: Frame-synced durations with +1-frame bias to avoid undershoot
  - Off: Uses `core.wait` for timing

### Triggers/Photodiode

- `port_open_send.py` sends event triggers when available. If no device is connected, warnings will print.
- A small white square can be drawn for photodiode timing (enabled by default in code).

### Data Output

- Saved under `logs/<ParticipantID>/<ParticipantID>_Experiment_logfile.csv`
- Fields include: Participant, Block, Trial_num, Response, Correct, RT, Jitter, Match, Sentence, Probe, Condition

## Parity Notes

- Fonts: Stimuli use Courier New, white, 24 px (online uses 0.6em).
- Keys and instructions are harmonized across both implementations.
- Block structure: 8 blocks; online separates via `trialsPerBlock`, in-person chunks stimuli evenly.

## Development Tips

- Press 's' to exit the in-person experiment and save a log file
- To switch timing mode quickly: use the GUI toggle on launch.
- If you need exact per-block counts in-person, adjust the slicing logic in `in-person/main.py`.
- To change stimulus fonts/sizes or colors, edit `in-person/main.py` `TextStim` definitions and `online/data_includes/main.js` CSS/Text settings.

## Citation

If using the in-person experiment framework, please cite:

PsychoPy: Peirce et al. (2019)

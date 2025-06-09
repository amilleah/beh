# PsychoPy Behavioral Experiment

Rapid stimulus presentation experiment with MEG/EEG trigger support for psychophysiology research.

## Experiment Design

### Task Structure
All trials have quit, 'q', and pause, 'p', functionality. 
Use 's' to unpause/exit the experiment.

- 8 blocks of randomized trials from `experiment.csv`

[+]   [blank screen]   [Stim1]   [blank screen]   [Stim2]     [blank screen until response]

- Timing is configurable in `experiment.py`.
- Expected response is keyboard input: '1' or '2'.
- Halfway through experiment, there is a block break that requires experimenter progression with keybord input 's'.
- Halfway through experiment, there is an feedback screen implemented, this can optionally be used to give more questions, or for providing fun facts for attention/engagement. 

### Hardware Integration
- **Triggers**: Automated MEG event markers via serial port
- **Photodiode**: Onset timing synchronization
- **Response**: Keyboard input with timing
- **Display**: Configurable fullscreen/windowed presentation

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure serial port (update in port_open_send.py)
ser.port = '/dev/cu.usbserial-XXXXX'  # Replace with your port
```

## Usage

### Setup
1. **Stimuli Files**: With CSV files in `stimuli/` directory:
   - `experiment.csv`: Main experimental trials
   - `practice.csv`: Practice session trials
   - `feedback.csv`: Optional break content

2. **Hardware**: Connect trigger device and update port configuration

3. **Launch**: `cd` to experiment folder and Run `python experiment.py`

### GUI Options
- **Participant ID**: Subject identifier for data logging
- **Fullscreen**: Toggle fullscreen presentation
- **Auto Respond**: Response simulation for testing

## Configuration

### Timing Parameters
```python
ONSET = 300      # Stimulus duration (ms)
OFFSET = 500     # Inter-stimulus interval (ms)
JITTER = (200, 800)  # Random inter-trial interval range (ms)
```

### Trigger Mapping
```python
condition_map_1 = {
    'condition_A': 'ch160',
    'condition_B': 'ch161',
    'condition_C': 'ch162',
    'condition_D': 'ch163'
}
```

### Response Keys
- **'1'**: Different response (left middle finger)
- **'2'**: Same response (left index finger)
- **'p'**: Pause experiment
- **'q'**: Quit experiment

## Data Output

### Logged Variables
- Trial-by-trial responses and reaction times
- Stimulus conditions and timing
- Accuracy metrics and performance feedback
- Hardware trigger timestamps

### File Structure
```
logs/                    # generated in the directory above beh/
├── [participant_id]/
│   └── [participant_id]_Experiment_logfile.csv
beh/
├── stimuli/
│   ├── experiment.csv
│   ├── practice.csv
│   └── feedback.csv
├── experiment.py
└── port_open_send.py
```

## Troubleshooting

### Debug Options
```python
verbose = True          # Console output
show_photodiode = True  # Stimulus onset marker, white square drawn in the corner of the screen
send_triggers = True    # Serial port triggers
```

## Citation

If using this experiment framework, please cite:
- PsychoPy: Peirce et al. (2019)
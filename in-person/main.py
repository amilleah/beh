import os
import sys
import time
import json
import random
import pandas as pd
from sklearn.utils import shuffle
from psychopy import core, visual, event, data, gui
from psychopy.hardware import keyboard  

ROOT = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(os.path.dirname(ROOT), 'logs')
sys.path.append(ROOT)

from port_open_send import sendTrigger 

CONFIG = {
    'experiment': {
        'totalBlocks': 8,
        'trialsPerBlock': 25,
        'duration': '10 minutes'
    },
    'timings': {
        'mask': 200,   # fixation
        'mask2': 200,  # blank before prime
        'prime': 300,  # first stimulus
        'mask3': 500,  # blank before target
        'target': 300, # second stimulus
        'feedback': 500
    },
    'jitter': {
        'min': 300,
        'max': 700,
        'step': 10
    },
    'keys': {
        'same': '2',
        'different': '1',
        'continue': 'space'
    }
}

# Event trigger mappings
condition_map_1 = {
    1: 'ch160',
    2: 'ch161',
    3: 'ch162',
    4: 'ch163'
}

condition_map_2 = {
    'type_1': 'ch165',
    'type_2': 'ch166'
}

# Key bindings
experiment_keys = ['s', 'p', 'q']  # continue, pause, quit
response_keys = ['1', '2', 'p', 'q']  # response options + controls

# GUI setup
dlg_info = {
    'Participant ID': '',
    'Fullscreen': False,
    'Auto respond?': False,
    'Frame rate?': True
}
order = ['Participant ID', 'Fullscreen', 'Auto respond?', 'Frame rate?']
dlg = gui.DlgFromDict(dictionary=dlg_info, title='Experiment Settings', order=order)
if not dlg.OK: 
    core.quit()

# Experiment settings
experiment_name = 'Experiment'
verbose = True
show_photodiode = True
send_triggers = True
participant_id = dlg_info['Participant ID']
fullscreen = dlg_info['Fullscreen']
auto_respond = dlg_info['Auto respond?']
use_frame_rate = dlg_info['Frame rate?']

# Warnings
if not show_photodiode: 
    print("PHOTODIODE IS OFF")
if not send_triggers: 
    print("EVENT TRIGGERS WILL NOT BE SENT")
if auto_respond: 
    print("SIMULATING RESPONSES...")
if use_frame_rate: 
    print("SIMULATING RESPONSES...")

# Display setup
win = visual.Window(
    monitor='default', 
    units='pix', 
    checkTiming=True, 
    fullscr=fullscreen, 
    color='#444444'
)

text = visual.TextStim(
    win,
    text='',
    height=24,           # approx 0.6em equivalent
    font='Courier New',
    wrapWidth=750,
    alignText='center',
    color='white'
)

fixation = visual.TextStim(
    win,
    text='+',
    height=24,
    font='Arial',
    wrapWidth=750,
    alignText='center',
    color='white'
)

photodiode = visual.Rect(
    win, width=57, height=57, 
    pos=[-483, 355], fillColor='white'
)

proceed = keyboard.Keyboard()
trial_clock = core.Clock()
win.mouseVisible = False

t0 = trial_clock.getTime()
print(f"Initialization time: {t0}")
print(f'Window size: {win.size}')

# Timing parameters (ms), aligned with online CONFIG
frame_time_ms = win.monitorFramePeriod * 1000
TIMINGS = CONFIG['timings']

def _make_jitter_values():
    return list(range(CONFIG['jitter']['min'], CONFIG['jitter']['max'] + 1, CONFIG['jitter']['step']))

jitter_values = _make_jitter_values()

# Instruction texts (harmonized with online HTML)
setup_text = "Please be patient as we set up the experiment..."
practice_instructions = (
    "PRACTICE\n\n"
    "Welcome to the experiment! This is a task investigating how we process rapidly presented SENTENCES.\n\n" 
    "Each trial will consist of pairs of sentences.\n\n"
    "Press RED with your INDEX FINGER if the pair are the SAME \n\n" 
    "Press BLUE with your MIDDLE FINGER if the pair are DIFFERENT.\n\n"
    "Please answer as quickly and accurately as possible. You will recieve feedback for this part.\n\n"
    "When you are ready, press either response button to continue."
)

main_instructions = (
    "EXPERIMENT\n\n"
    "We are now ready to start the experiment. You will see the same types of trials as in practice, but you will not receive feedback.\n\n"
    "REMEMBER: Press RED with your INDEX FINGER if they are the SAME, BLUE with your MIDDLE FINGER if they are DIFFERENT.\n\n"
    "When you are ready, press either response button to begin."
)

end_text = (
    "EXPERIMENT COMPLETE\n\n"
    "Thank you for participating in this study! Please remain still while we save the recording..."
)
pause_text = "Experiment paused. Wait for experimenter to continue."
progress_text = "Press any button to continue."

# Load stimuli
try:
    stimuli = pd.read_csv(os.path.join(ROOT, 'stimuli', 'stimuli.csv'))
    practice = pd.read_csv(os.path.join(ROOT, 'stimuli', 'practice.csv'))
    feedback = pd.read_csv(os.path.join(ROOT, 'stimuli', 'feedback.csv'))  # optional fun facts during break
except FileNotFoundError as e:
    print(f"Stimulus file not found: {e}")
    core.quit()

# Block setup 
n_blocks = CONFIG['experiment']['totalBlocks']
n_trials = len(stimuli)
stimuli = shuffle(stimuli, random_state=None)

# Slice into n_blocks roughly equal parts
block_size = max(1, n_trials // n_blocks)
blocks = [shuffle(stimuli[i*block_size:(i+1)*block_size], random_state=None) for i in range(n_blocks)]
blocks = shuffle(blocks, random_state=None)

practice = shuffle(practice)
feedback_items = shuffle(feedback)

def is_correct_response(trial, response):
    try:
        match = str(trial.get('Match', '')).strip().lower()
        if match in ('match', '1', 'true'):
            correct = CONFIG['keys']['same']
        elif match in ('mismatch', '0', 'false'):
            correct = CONFIG['keys']['different']
        else:
            correct = CONFIG['keys']['same'] if str(trial['Sentence']) == str(trial['Probe']) else CONFIG['keys']['different']
    except Exception:
        correct = CONFIG['keys']['same'] if str(trial['Sentence']) == str(trial['Probe']) else CONFIG['keys']['different']
    return correct == response

def get_correct_response(trial):
    try:
        match = str(trial.get('Match', '')).strip().lower()
        if match in ('match', '1', 'true'):
            return CONFIG['keys']['same']
        if match in ('mismatch', '0', 'false'):
            return CONFIG['keys']['different']
        return CONFIG['keys']['same'] if str(trial['Sentence']) == str(trial['Probe']) else CONFIG['keys']['different']
    except Exception:
        return CONFIG['keys']['same'] if str(trial['Sentence']) == str(trial['Probe']) else CONFIG['keys']['different']

def present_text(text_content='', keys=experiment_keys):
    text.setText(text_content)
    text.draw()
    win.flip()
    
    key_response = event.waitKeys(keyList=keys)
    if key_response and key_response[0] == 'q': 
        present_text(end_text, ['s'])
        core.quit()
    elif key_response and key_response[0] == 'p': 
        present_text(pause_text, ['s'])
        present_text(progress_text, ['1', '2'])
    
    return key_response[0] if key_response else None

def present_stimulus(stimulus_text, timing=None, trigger=None, keys=None):
    if verbose and stimulus_text == '+':
        print(f"Current Trial: {trial_num} / {n_trials}")
    elif verbose and stimulus_text:
        print(f"Presenting stimulus: {stimulus_text}")
    
    text.setText(stimulus_text)
    start_time = time.time()
    
    response_keys_list = keys + ['p', 'q'] if keys is not None else ['p', 'q']
    
    # Auto-response mode
    if auto_respond and keys is not None:
        if use_frame_rate and timing:
            frames = int(((timing or 0) / (win.monitorFramePeriod * 1000))) + 1
            for frameN in range(frames):
                text.draw()
                if show_photodiode:
                    photodiode.draw()
                win.flip()
                if frameN == 0 and trigger and send_triggers:
                    sendTrigger(channel=trigger, duration=0.02)
        elif timing:
            text.draw()
            if show_photodiode:
                photodiode.draw()
            win.flip()
            if trigger and send_triggers:
                sendTrigger(channel=trigger, duration=0.02)
            core.wait(timing/1000.0)
        response = str(random.randint(1, 2))
        auto_rt = random.uniform(0.4, 0.6)
        core.wait(auto_rt)
        end_time = time.time()
        
        if verbose and stimulus_text:
            print(f"Stimulus duration: {(end_time - start_time) * 1000:.2f} ms")
            print(f"Response: {response}")
            if 'accuracy' in globals() and trial_num > 0:
                print(f"Current accuracy: {accuracy:.1f}%")
            print(f'RT: {(end_time - start_time) * 1000:.2f} ms')
        return response, end_time - start_time
    
    response = None
    response_time = None
    
    event.clearEvents()
    
    # Show stimulus for specified duration
    if timing:
        if use_frame_rate:
            frames = int((timing / (win.monitorFramePeriod * 1000))) + 1
            for frameN in range(frames):
                text.draw()
                if show_photodiode:
                    photodiode.draw()
                win.flip()
                if frameN == 0 and trigger and send_triggers:
                    sendTrigger(channel=trigger, duration=0.02)
        else:
            text.draw()
            if show_photodiode:
                photodiode.draw()
            win.flip()
            if trigger and send_triggers:
                sendTrigger(channel=trigger, duration=0.02)
            core.wait(timing/1000.0)

    # If this stimulus expects a response, blank the screen right after timing window
    if timing and keys is not None:
        win.flip()

    end_time = time.time()
    
    if verbose and timing is not None and stimulus_text not in ["+", ""]:
        print(f"Stimulus duration: {(end_time - start_time) * 1000:.2f} ms")
    
    # Wait for response if keys specified
    if keys is not None and response is None:
        key_response = event.waitKeys(keyList=response_keys_list)
        if key_response:
            response = key_response[0]
            response_time = time.time() - start_time
    
    if keys is not None and response in ['1', '2']:
        rt_ms = response_time * 1000 if response_time else (end_time - start_time) * 1000
        if verbose:
            print(f"Response: {response}")
            if 'accuracy' in globals() and trial_num > 0:
                print(f"Current accuracy: {accuracy:.1f}%")
            print(f'RT: {rt_ms:.2f} ms')
    
    if keys is None and verbose and timing is not None:
        if stimulus_text == "":
            print(f"ISI: {(end_time - start_time) * 1000:.2f} ms")
    
    # Handle control keys
    if response:
        if response == 'q':
            print('Experiment quit...')
            present_text(end_text, keys=['s'])
            core.quit()
        elif response == 'p':
            print('Experiment paused...')
            present_text(pause_text, ['s'])
            present_text(progress_text, ['1', '2'])
    
    return response, response_time if response_time else (end_time - start_time)

def present_feedback(text_content, keys=response_keys):
    text.setText(text_content)
    text.draw()
    win.flip()
    
    response = event.waitKeys(keyList=keys)
    
    if response[0] == 'q':
        present_text(end_text, ['s'])
        core.quit()
    elif response[0] == 'p':
        present_text(pause_text, ['s'])
        present_text(progress_text, ['1', '2'])
    elif response[0] == '2':  # Positive response
        feedback_item = feedback_items.sample(1).iloc[0]
        present_text(
            text=str(feedback_item['prompt'] + "\n\n\n\n(Press any button to continue)"), 
            keys=['1', '2', 's', 'q']
        )
        present_text(feedback_item['content'], keys=['1', '2', 's', 'q'])

def run_block(block_data, show_practice_feedback=False):
    global trial_num, total_correct
    
    for _, trial in block_data.iterrows():
        # Get trigger conditions (from numeric Condition)
        try:
            cond_val = int(trial.get('Condition'))
        except Exception:
            # Fallback if Condition is missing or non-numeric
            cond_val = None
        trigger_1 = condition_map_1.get(cond_val)
        
        # Present trial sequence
        present_stimulus("+", timing=TIMINGS['mask'], trigger=None, keys=None)  # fixation
        present_stimulus("", timing=TIMINGS['mask2'], trigger=None, keys=None)   # blank
        present_stimulus(
            trial['Sentence'], 
            timing=TIMINGS['prime'], 
            trigger=trigger_1, 
            keys=None
        )
        present_stimulus("", timing=TIMINGS['mask3'], trigger=None, keys=None)  # blank
        
        response, rt = present_stimulus(
            trial['Probe'], 
            timing=TIMINGS['target'], 
            trigger=None, 
            keys=response_keys
        )
        
        # Inter-trial interval
        jitter = random.choice(jitter_values)
        # Optional practice feedback display
        if show_practice_feedback and response in ['1','2']:
            correct = is_correct_response(trial, response)
            fb_text = 'Correct' if correct else 'Wrong'
            fb_stim = visual.TextStim(
                win,
                text=fb_text,
                height=20,
                font='Courier New',
                wrapWidth=900,
                alignText='center',
                color='white'
            )
            if use_frame_rate:
                frames_fb = int((TIMINGS['feedback'] / (win.monitorFramePeriod * 1000))) + 1
                for _ in range(frames_fb):
                    fb_stim.draw()
                    if show_photodiode:
                        photodiode.draw()
                    win.flip()
            else:
                fb_stim.draw()
                if show_photodiode:
                    photodiode.draw()
                win.flip()
                core.wait(TIMINGS['feedback']/1000.0)
        present_stimulus("", timing=jitter, keys=None)
        
        # Score response
        correct = is_correct_response(trial, response)
        total_correct += int(correct)

        if verbose and response in response_keys:
            print(f"Correct answer: {get_correct_response(trial)}")
            print(f"Correct: {int(correct)}")
            print()

        # Log data
        if experiment_handler:
            experiment_handler.addData('Participant', participant_id)
            experiment_handler.addData('Trial_num', trial_num)
            experiment_handler.addData('Block', block_num)
            experiment_handler.addData('Response', response)
            experiment_handler.addData('Correct', correct)
            experiment_handler.addData('RT', rt)
            experiment_handler.addData('Jitter', jitter)
            for col in ('Match', 'Sentence', 'Probe', 'Condition'):
                if col in trial.index:
                    experiment_handler.addData(col, trial[col])
            
            experiment_handler.nextEntry()
        
        trial_num += 1

# Main experiment
present_text(setup_text, ['s', 'q'])
print("STARTING PRACTICE SESSION...")
present_text(practice_instructions, ['1', '2', 'p', 'q'])

trial_num = 0
total_correct = 0
experiment_handler = None

# Practice session
try:
    run_block(practice, show_practice_feedback=True)
    accuracy = (total_correct / len(practice)) * 100
    present_text(
        f"Practice session complete.\n\n"
        f"Your accuracy: {accuracy:.1f}%.\n\n"
        f"Press either button when ready to continue.", 
        ['1', '2', 's', 'q']
    )
    print("PRACTICE SESSION COMPLETE")
except Exception as e:
    print(f"Error in practice: {e}")

# Setup data logging
if participant_id:
    log_dir = os.path.join(LOGS, participant_id)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'{participant_id}_{experiment_name}_logfile')
    experiment_handler = data.ExperimentHandler(
        dataFileName=log_file, 
        autoLog=False, 
        savePickle=False
    )

present_text(setup_text, ['s', 'q'])
present_text(main_instructions, ['1', '2', 'p', 'q'])

# Reset counters for main experiment
trial_num = 0
block_num = 1
total_correct = 0
experiment_start = time.time()

# Main experiment blocks
for block_num, block in enumerate(blocks, start=1):
    try:
        run_block(block)
        accuracy = (total_correct / trial_num) * 100
        
        if block_num == len(blocks) // 2:  # Halfway point
            present_text(
                f"End of block {block_num}.\n\n"
                f"Your accuracy: {accuracy:.1f}%.\n\n"
                f"Let the experimenter know when ready to continue.", 
                experiment_keys
            )
            present_feedback(
                "You're at the halfway point. Great job!"
                "Want a fun fact? Press SAME for YES, DIFFERENT for NO.", 
                ['1', '2']
            )
            present_text(
                f"Start of block {block_num+1}.\n\n"
                f"Press any button when ready to continue.", 
                ['1', '2', 's', 'q']
            )
        elif block_num != len(blocks):
            present_text(
                f"End of block {block_num}.\n\n"
                f"Your accuracy: {accuracy:.1f}%.\n\n"
                f"Press either button when ready to continue.", 
                ['1', '2', 's', 'q']
            )
        else:
            print("EXPERIMENT COMPLETE")
            
    except Exception as e:
        print(f"Error in block {block_num}: {e}")

# Experiment end
try:
    final_accuracy = (total_correct / trial_num) * 100
    present_text(
        f"The experiment is complete! Thank you for participating!\n\n"
        f"Your final accuracy: {final_accuracy:.1f}%.\n\n"
        f"Please sit still while we save the recording...", 
        ['s']
    )
except:
    present_text(end_text, ['s'])
finally:
    experiment_end = time.time()
    experiment_duration = experiment_end - experiment_start
    
    if verbose:
        print(f"Total experiment time: {experiment_duration:.2f} seconds")
        print(f"Total experiment time: {experiment_duration/60:.2f} minutes")
        print(f"Final accuracy: {final_accuracy:.1f}%")
    
    core.quit()

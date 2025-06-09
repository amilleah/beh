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

# Event trigger mappings
condition_map_1 = {
    'condition_A': 'ch160', 
    'condition_B': 'ch161',
    'condition_C': 'ch162',
    'condition_D': 'ch163' 
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
    'Auto respond?': False
}
order = ['Participant ID', 'Fullscreen', 'Auto respond?']
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

# Warnings
if not show_photodiode: 
    print("PHOTODIODE IS OFF")
if not send_triggers: 
    print("EVENT TRIGGERS WILL NOT BE SENT")
if auto_respond: 
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
    win, text='', height=25, font='Arial', 
    wrapWidth=700, alignText='center', color='white'
)

fixation = visual.TextStim(
    win, text='', height=30, font='Arial', 
    wrapWidth=700, alignText='center', color='white'
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

# Timing parameters (ms)
frame_time_ms = win.monitorFramePeriod * 1000
ONSET = 300
OFFSET = 500
JITTER = (200, 800)

# Instruction texts
setup_text = "Please be patient as we set up the experiment..."
practice_instructions = """Welcome to the practice session! 

You will see pairs of items presented rapidly. 
Press '2' with your LEFT INDEX FINGER if they are the SAME. 
Press '1' with your LEFT MIDDLE FINGER if they are DIFFERENT. 

This practice session will be brief. 
When you are ready, press either button to continue."""

main_instructions = """This is the main experiment. 

You will see pairs of items presented rapidly. 
Press '2' with your LEFT INDEX FINGER if they are the SAME. 
Press '1' with your LEFT MIDDLE FINGER if they are DIFFERENT. 

When you are ready, press either button to continue."""

end_text = "The experiment is now over! Thank you for your participation! Please remain still while we save the recording..."
pause_text = "Experiment paused. Wait for experimenter to continue."
progress_text = "Press any button to continue."

# Load stimuli
try:
    stimuli = pd.read_csv('stimuli/experiment.csv')
    practice = pd.read_csv('stimuli/practice.csv')
    feedback = pd.read_csv('stimuli/feedback.csv') # e.g., implemented here as optional fun facts during break 
except FileNotFoundError as e:
    print(f"Stimulus file not found: {e}")
    core.quit()

# Block setup
n_blocks = 8 
n_trials = len(stimuli)
stimuli = shuffle(stimuli)
blocks = [shuffle(stimuli[i*(n_trials//n_blocks):(i+1)*(n_trials//n_blocks)]) 
          for i in range(n_blocks)]
blocks = shuffle(blocks)

practice = shuffle(practice)
feedback_items = shuffle(feedback)

# Helper functions
def is_correct_response(trial, response):
    return trial['correct_response'] == response

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
    text.draw()
    if show_photodiode:
        photodiode.draw()
    
    start_time = time.time()
    win.flip()
    
    # Send triggers after stimulus onset
    if trigger and send_triggers:
        trial_clock.reset()
        triggers = trigger if isinstance(trigger, (list, tuple)) else [trigger]
        for t in triggers:
            if t is not None:
                sendTrigger(channel=t, duration=0.02)
                core.wait(0.01)
                if verbose:
                    print(f"Sending trigger: {t}")
    
    response_keys_list = keys + ['p', 'q'] if keys is not None else ['p', 'q']
    
    # Auto-response mode
    if auto_respond and keys is not None:
        core.wait(timing/1000.0)
        win.flip()
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
        core.wait(timing/1000.0)
    
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
        if stimulus_text == "" and timing not in [ONSET, OFFSET]:
            print(f"Jitter duration: {(end_time - start_time) * 1000:.2f} ms")
    
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

def run_block(block_data):
    global trial_num, total_correct
    
    for _, trial in block_data.iterrows():
        # Get trigger conditions
        trigger_1 = condition_map_1.get(trial['condition'])
        
        # Present trial sequence
        present_stimulus("+", timing=ONSET, trigger=None, keys=None)  # fixation
        present_stimulus("", timing=ONSET, trigger=None, keys=None)   # blank
        present_stimulus(
            trial['stimulus_1'], 
            timing=ONSET, 
            trigger=trigger_1, 
            keys=None
        )
        present_stimulus("", timing=OFFSET, trigger=None, keys=None)  # blank
        
        response, rt = present_stimulus(
            trial['stimulus_2'], 
            timing=ONSET, 
            trigger=None, 
            keys=response_keys
        )
        
        # Inter-trial interval
        jitter = random.uniform(*JITTER)
        present_stimulus("", timing=jitter, keys=None)
        
        # Score response
        correct = is_correct_response(trial, response)
        total_correct += int(correct)

        if verbose and response in response_keys:
            print(f"Correct answer: {trial['correct_response']}")
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
            
            for column in trial.index:
                experiment_handler.addData(column, trial[column])
            
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
    run_block(practice)
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
                "You're at the halfway point. Great job! "
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
        f"Please sit tight while we save the recording...", 
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

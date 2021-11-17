import os
import subprocess
import pathlib
import time
import sys
from numpy.core.shape_base import block
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from random import randint
import random
from datetime import datetime

def run_make():
    p_status, p_output = subprocess.getstatusoutput('make')
    if p_status != 0:
        print(p_output)
        raise Exception("Make did not run succesfully")

def start_simulation(bin_file, input_file, output_file):
    if not os.path.isfile(bin_file):
        print(f'Python: Bin file does not exist at {bin_file}')
        
    subprocess.Popen([
        bin_file, 
        input_file, 
        output_file
        ]
        # , stdout=subprocess.DEVNULL #para evitar que salga a consola
        )

def plot_trials(output_file, block_count):
    plt.close('all')
    plt.ion()
    plt.show()
    # estructura: trial, x, y, z
    names = ['trial', 'timeMs', 'x', 'y', 'z']
    var_names = ['angle', 'vmr', 'blockN','trialSuccess']
    # TO DO: filtrar trialSuccess = 0
    names += var_names
    df = pd.read_csv(output_file, names=names, index_col=False)
    df['x'] = -df['x']*100
    df['y'] = df['y']*100
    fig, axs = plt.subplots(1,block_count, sharey=True)
    grouped = df.groupby(['trial','blockN', 'vmr'])
    for ax in axs:
        ax.axis('equal')
        ax.set_box_aspect(1)
    
    for (trial, blockN, vmr), group in grouped:
        group.plot(x='y', y='x', ax=axs[blockN], label=f'trial {trial}', legend=False)
    
    for (blockN, vmr), group in df.groupby(['blockN', 'vmr']):
        trial_count = len(group.trial.unique())
        axs[blockN].set_title(f'vmr: {vmr} trials: {trial_count}')

    plt.draw()
    plt.pause(1)
    return

def change_variables(input_file, variables_for_trial):
    f = open(input_file, "w")
    variables_str = " ".join([str(i) for i in variables_for_trial])
    print(variables_str, file = f)
    f.close()
    print("Python: finished writing input file")
    return

def get_variables():
    var = {}
    var[len(var)] = get_variables_block(N=12, vmr=0)
    var[len(var)] = get_variables_block(N=12, vmr=1)
    var[len(var)] = get_variables_block(N=12, vmr=0)
    return var

def get_variables_block(N, vmr):
    block = {}
    positions = [0, 1, 2, 3, 4, 5]*N
    angles = [i*60 for i in positions]
    random.shuffle(angles)    
    block["vmr"] = vmr
    block["n"] = len(angles)
    block["angles"] = angles
    return block

def start_controller(input_file, output_file, variables):
    last_mod_time = None # epoch float

    block_count = len(variables) # cant de bloques
    # Consumo de memoria/CPU: htop -p "$(pgrep -d , "python|test")"
        
    for blockN in variables:
        block = variables[blockN]
        angles = block['angles']
        initial_block_len = block['n']
        vmr = block['vmr']
        i = 0
        while (i < len(angles) and i < initial_block_len*1.1):
            print(f'\nPython: blockN: {blockN} trial:{i}')
            angle = angles[i]
            trial_variables = [angle, vmr, blockN]
            change_variables(input_file, trial_variables)

            last_mod_time = waitForFileChange(output_file, last_mod_time)

            try:
                plot_trials(output_file, block_count)
            except Exception as e:
                print(f"Python: WARNING plot_trials error: {str(e)}")

            if not lastTrialSuccess(output_file):
                angles.append(angle)
                print(f"Trial {i} failed. Adding new trial for block {blockN} with angle {angle}")
            i += 1
    print("Python: Trials done. Closing simulation and removing input file")
    os.remove(input_file)
    time.sleep(5)
    input("Python: Press enter to finish script")

def lastTrialSuccess(output_file):
    f = open(output_file, "r")
    last_char = f.read()[-2]
    f.close()
    trialSuccess = int(last_char)
    return trialSuccess

def waitForFileChange(output_file, last_mod_time):
    while not os.path.isfile(output_file): # chequea que exista el output
        time.sleep(0.1)

    fname = pathlib.Path(output_file)
    while True:
        mod_time = fname.stat().st_mtime 
        if (last_mod_time != mod_time) and (time.time() - mod_time > 0.2): 
            print('Python: output file changed')
            return mod_time
        time.sleep(0.2)
        


if __name__ == "__main__":
    try:
        run_make()
        data_path = os.path.join(sys.path[0], 'data')
        os.makedirs(data_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        subject_name = input("Nombre sel sujeto: ")
        filepreffix = f'vmr_{subject_name}_{timestamp}'
        input_file = os.path.join(data_path, f'{filepreffix}_in.csv')
        output_file = os.path.join(data_path, f'{filepreffix}_out.csv')

        bin_file = os.path.join( sys.path[0], '../../bin/lin-x86_64/vmr_test1')

        variables = get_variables()
        start_simulation(bin_file, input_file, output_file)
        start_controller(input_file, output_file, variables)
    except KeyboardInterrupt:
        print('\nPython: Stopping due to KeyboardInterrupt')
    except Exception as e:
        print(f"Python error: {str(e)}")
        raise e





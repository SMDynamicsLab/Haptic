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
        print(f'Bin file does not exist at {bin_file}')

    subprocess.Popen([
        bin_file, 
        input_file, 
        output_file
        ]
        # , stdout=subprocess.DEVNULL #para evitar que salga a consola
        )

def plot_trials(output_file):
    plt.close('all')
    plt.ion()
    plt.show()
    # estructura: trial, x, y, z
    names = ['trial', 'x', 'y', 'z']
    var_names = ['angle', 'visual_feedback', 'force']
    names += var_names
    df = pd.read_csv(output_file, names=names, index_col=False)
    df['x'] = -df['x']
    fig, axs = plt.subplots(2)

    x = np.linspace(df['x'].min(), df['x'].max(), 100)
    y = []
    for trial, group in df.groupby('trial'):
        group.plot(x='y', y='x', ax=axs[0], label=f'trial {trial}')
    #     y.append(np.interp(x, df[df['trial']==trial]['x'], df[df['trial']==trial]['y']))
    # midy = [np.mean([y[j][i] for j in range(len(df['trial'].unique()))]) for i in range(100)]
    # stdy = [np.std([y[j][i] for j in range(len(df['trial'].unique()))]) for i in range(100)]
    # axs[1].plot(x, midy, '--', c='black')
    # axs[1].plot(x, [midy[i]+stdy[i] for i in range(100)], '--', c='red')
    # axs[1].plot(x, [midy[i]-stdy[i] for i in range(100)], '--', c='red')
    plt.draw()
    plt.pause(1)
    return

def change_variables(input_file, variables_for_trial):
    f = open(input_file, "w")
    variables_str = " ".join([str(i) for i in variables_for_trial])
    print(variables_str, file = f)
    f.close()
    return

def get_variables(variables_array = []):
    variables_array += get_variables_block(N=1, visual_feedback=1, force=0)
    variables_array += get_variables_block(N=1, visual_feedback=0, force=0)
    variables_array += get_variables_block(N=1, visual_feedback=0, force=1)
    variables_array += get_variables_block(N=1, visual_feedback=0, force=0) 
    print(len(variables_array))
    return variables_array

def get_variables_block(N, force, visual_feedback):
    angles = [0, 1, 2, 3, 4, 5]*N
    random.shuffle(angles)
    variables = [[angle*60, visual_feedback, force] for angle in angles]
    return variables

def start_controller(input_file, output_file, variables):
    fname = pathlib.Path(output_file)
    last_mod_time = None # epoch float
    output_exists = os.path.isfile(output_file)
    trial = 1
    # Consumo de memoria/CPU: htop -p "$(pgrep -d , "python|test")"
    while True:
        # no sleep 99% CPU
        # time.sleep(0.001) #~9% CPU
        # time.sleep(0.01) # ~2% CPU
        time.sleep(0.1)
        if output_exists:
            mod_time = fname.stat().st_mtime 
            if last_mod_time != mod_time:
                print('file changed')
                last_mod_time = mod_time
                plot_trials(output_file)
                change_variables(input_file, variables[trial])
                print('len vars = ', len(variables), 'trial # = ', trial)
                trial+=1
        else:
            output_exists = os.path.isfile(output_file)

if __name__ == "__main__":
    try:
        run_make()
        data_path = os.path.join(sys.path[0], 'data')
        os.makedirs(data_path, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        input_file = os.path.join(data_path, f'in_{timestamp}.csv')
        output_file = os.path.join(data_path, f'out_{timestamp}.csv')

        bin_file = os.path.join( sys.path[0], '../../bin/lin-x86_64/vmr_test1')

        variables = get_variables()
        change_variables(input_file, variables[0]) # first trial
        start_simulation(bin_file, input_file, output_file)
        start_controller(input_file, output_file, variables)
    except KeyboardInterrupt:
        print('\nStopping due to KeyboardInterrupt')
    except Exception as e:
        print(f"Python error: {str(e)}")





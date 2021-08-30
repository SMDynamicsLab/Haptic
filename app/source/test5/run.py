import os
import subprocess
import pathlib
import time
import sys
from numpy.core.shape_base import block
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

def run_make():
    p_status, p_output = subprocess.getstatusoutput('make')
    if p_status != 0:
        print(p_output)

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
    df = pd.read_csv(output_file, names=names)
    x_min = df['x'].min()
    df['x'] = df['x']-x_min
    fig, ax = plt.subplots()
    for trial, group in df.groupby('trial'):
        group.plot(x='x', y='y', ax=ax, label=f'trial {trial}')
    plt.draw()
    plt.pause(1)
    return

def change_variables(input_file):
    return

def start_controller(input_file, output_file):
    fname = pathlib.Path(output_file)
    last_mod_time = None # epoch float
    output_exists = os.path.isfile(output_file)
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
                change_variables(input_file)
        else:
            output_exists = os.path.isfile(output_file)

if __name__ == "__main__":
    run_make()

    data_path = os.path.join(sys.path[0], 'data')
    os.makedirs(data_path, exist_ok=True)
    input_file = os.path.join(data_path, 'in.csv')
    output_file = os.path.join(data_path, 'out.csv')

    bin_file = os.path.join( sys.path[0], '../../bin/lin-x86_64/test5')

    start_simulation(bin_file, input_file, output_file)
    try:
        start_controller(input_file, output_file)
    except KeyboardInterrupt:
        print('\nStopping due to KeyboardInterrupt')





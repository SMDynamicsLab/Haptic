import os
import subprocess
import pathlib
import time
import sys
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np

def run_make():
    p_status, p_output = subprocess.getstatusoutput('make')
    if p_status != 0:
        print(p_output)

def start_simulation(bin_file, input, output):
    if not os.path.isfile(bin_file):
        print(f'Bin file does not exist at {bin_file}')

    subprocess.Popen([
        bin_file, 
        input, 
        output
        ]
        # , stdout=subprocess.DEVNULL #para evitar que salga a consola
        )

def plot_trials(output):
    # estructura trial, x, y, z
    names = ['trial', 'x', 'y', 'z']
    df = pd.read_csv(output, names=names)
    x_min = df['x'].min()
    df['x'] = df['x']-x_min
    fig, ax = plt.subplots()
    for trial, group in df.groupby('trial'):
        group.plot(x='x', y='y', ax=ax, label=f'trial {trial}')
    plt.show()
    print(df.head)
    return

def change_variables(input):
    print(input)
    return

def start_controller(input, output):
    fname = pathlib.Path(output)
    output_mod_time = None # epoch float

    # Consumo de memoria/CPU: htop -p "$(pgrep -d , "python|test")"
    while True:
        # no sleep 99% CPU
        # time.sleep(0.001) #~9% CPU
        time.sleep(0.01) # ~2% CPU
        if os.path.isfile(output):
            mod_time = fname.stat().st_mtime 
            if output_mod_time != mod_time:
                print('file changed')
                output_mod_time = mod_time
                plot_trials(output)
                change_variables(input)

if __name__ == "__main__":
    run_make()

    data_path = os.path.join(sys.path[0], 'data')
    os.makedirs(data_path, exist_ok=True)
    input = os.path.join(data_path, 'in.csv')
    output = os.path.join(data_path, 'out.csv')

    bin_file = os.path.join( sys.path[0], '../../bin/lin-x86_64/test6')

    start_simulation(bin_file, input, output)
    start_controller(input, output)





import os
import subprocess
import pathlib
import time
import sys
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
from plot.plot import plot
from zipfile import ZipFile


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

def change_variables(input_file, variables_for_trial):
    f = open(input_file, "w")
    variables_str = " ".join([str(i) for i in variables_for_trial])
    print(variables_str, file=f)
    f.close()
    print(f"Python: finished writing input file with {variables_for_trial}")
    return


def vmr_get_variables(type='experiment', exp_choice=None):
    var = {}
    positions_arr = [0, 1, 2, 3, 4, 5]

    if exp_choice == None:
        if type is 'demo':
            for i in positions_arr:
                var[len(var)] = vmr_get_variables_block(N=1, vmr=0, positions_arr=[i])
                var[len(var)] = vmr_get_variables_block(N=2, vmr=1, positions_arr=[i+1])  # el +1 es porque vmr gira

        elif type is 'experiment':
            N = 12
            for vmr in [0, 1, 0]:
                var[len(var)] = vmr_get_variables_block(N=N, vmr=vmr, positions_arr=positions_arr)

    elif exp_choice == 'vt':
        if type is 'demo':
            N = 1 #
            position = 0
            for vmr, sound in [(0,1), (0,2), (0,3), (1,3), (1,2), (1,1)]:
                if vmr:
                    positions_arr = [position + 1] # el + 1 es porque vmr gira
                else:
                    positions_arr = [position] # el + 1 es porque vmr gira
                print(f"vmr: {vmr}, positions arr = {positions_arr}")
                var[len(var)] = vmr_get_variables_block(N=N, vmr=vmr, positions_arr=positions_arr, sound=sound)

        elif type is 'experiment':
            N = 20 
            position = 0
            for vmr, sound in [(0,1),(1,1),(0,1),(0,2),(1,2),(0,2),(0,3),(1,3),(0,3)]:
                if vmr:
                    positions_arr = [position + 1] # el + 1 es porque vmr gira
                else:
                    positions_arr = [position] # el + 1 es porque vmr gira
                var[len(var)] = vmr_get_variables_block(N=N, vmr=vmr, positions_arr=positions_arr, sound=sound)


    elif exp_choice == 'ft':
        # if type is 'demo': # demo de todas las fuerzas
        #     N = 1 #
        #     positions_arr = [0]
        #     sound = 1
        #     for force_type in [0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0]:
        #         force = int(force_type > 0)
        #         var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)
        
        # elif type is 'experiment': # exp piloto de todas las fuerzas
        #     N = 10
        #     positions_arr = [0]
        #     sound = 1
        #     for force_type in [0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0]:
        #         force = int(force_type > 0)
        #         var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)

        #-------------------

        # if type is 'demo': # demo de las fuerzas 1, 2, 3 y 6
        #             N = 1 #
        #             positions_arr = [0]
        #             sound = 1
        #             for force_type in [0, 1, 0, 2, 0, 3, 0, 6, 0]:
        #                 force = int(force_type > 0)
        #                 var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)

        # elif type is 'experiment': # exp piloto de las fuerzas 1, 2, 3 y 6
        #     N = 15
        #     positions_arr = [0]
        #     sound = 1
        #     for force_type in [0, 1, 0, 2, 0, 3, 0, 6, 0]:
        #         force = int(force_type > 0)
        #         var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)        

        #-------------------

        if type is 'demo': # demo de dos periodos y la fuerza 1 (del paper)
            N = 1 #
            positions_arr = [0]
            for force_type, sound in [(0,1), (0,3), (1,3), (1,1)]:
                force = int(force_type > 0)
                var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)

        # elif type is 'experiment': # exp piloto de dos periodos (corto a largo), 30 trials y la fuerza 1 (del paper)
        #     N = 30
        #     positions_arr = [0]
        #     sound = 1
        #     for force_type, sound in [(0,1),(1,1),(0,1),(0,3),(1,3),(0,3)]:
        #         force = int(force_type > 0)
        #         var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)   
        elif type is 'experiment': # exp piloto de dos periodos (largo a corto), 30 trials y la fuerza 1 (del paper)
            N = 30
            positions_arr = [0]
            sound = 1
            for force_type, sound in [(0,3),(1,3),(0,3),(0,1),(1,1),(0,1)]:
                force = int(force_type > 0)
                var[len(var)] = vmr_get_variables_block(N=N, vmr=force, positions_arr=positions_arr, sound=sound, force_type=force_type)   

    elif exp_choice == 'vft':
        sound = 1
        position = 0
        if type is 'demo':
            N = 1

        elif type is 'experiment':
            N = 30

        for vmr, force_type in [(0,0),(0,1),(0,0),(1,0),(0,0)]:
            if vmr:
                positions_arr = [position + 1] # el + 1 es porque vmr gira
            else:
                positions_arr = [position] # el + 1 es porque vmr gira
            var[len(var)] = vmr_get_variables_block(N=N, vmr=vmr, positions_arr=positions_arr, sound=sound, force_type=force_type)

    return var


def vmr_get_variables_block(N, vmr, positions_arr, sound=0, force_type=0):
    block = {}
    positions = positions_arr * N
    angles = [i * 60 for i in positions]
    random.shuffle(angles)
    block["vmr"] = vmr
    block["n"] = len(angles)
    block["angles"] = angles
    block["sound"] = sound
    block["force_type"] = force_type
    return block


def vmr_start_controller(input_file, output_file, variables, type='experiment'):
    if type is 'demo':
        max_per_block = float('inf')
    else:
        max_per_block = 1.1

    last_mod_time = None  # epoch float

    block_count = len(variables)  # cant de bloques
    # Consumo de memoria/CPU: htop -p "$(pgrep -d , "python|test")"

    for blockN in variables:
        block = variables[blockN]
        angles = block['angles']
        initial_block_len = block['n']
        vmr = block['vmr']
        sound = block['sound']
        force_type = block['force_type']
        i = 0
        while i < len(angles):
            print(f'\nPython: blockN: {blockN} trial:{i}')
            angle = angles[i]
            trial_variables = [angle, vmr, blockN, sound, force_type]
            change_variables(input_file, trial_variables)

            last_mod_time = waitForFileChange(output_file, last_mod_time)

            if not lastTrialSuccess(output_file):
                print(f"Python: Trial {i} for block {blockN} failed.")
                if len(angles) + 1 <= initial_block_len * max_per_block:
                    angles.append(angle)
                    print(f"Python: Adding new trial for block {blockN} with angle {angle}.")
            i += 1
    print("Python: Trials done. Closing simulation and removing input file")
    for file in [input_file]:
        if os.path.exists(file):
            os.remove(file) 

def lastTrialSuccess(output_file):
    f = open(output_file, "r")
    last_char = f.read()[-2]
    f.close()
    trialSuccess = int(last_char)
    return trialSuccess


def waitForFileChange(output_file, last_mod_time):
    while not os.path.isfile(output_file):  # chequea que exista el output
        time.sleep(0.1)

    fname = pathlib.Path(output_file)
    while True:
        mod_time = fname.stat().st_mtime
        if (last_mod_time != mod_time) and (time.time() - mod_time > 0.2):
            print('Python: output file changed')
            return mod_time
        time.sleep(0.2)


def run(bin_file, input_file, output_file, plot_file=None, type='experiment'):
    try:
        variables = vmr_get_variables(type=type)
        start_simulation(bin_file, input_file, output_file)
        vmr_start_controller(input_file, output_file, variables, type=type)

        time.sleep(5)
        if type == 'experiment':
            try:
                plot(output_file, plot_file)
            except Exception as e:
                print(f"Python: WARNING plot error: {str(e)}")

        input("Python: Press enter to finish")

    except KeyboardInterrupt:
        print('\nPython: Stopping due to KeyboardInterrupt')
    except Exception as e:
        print(f"Python error: {str(e)}")
        raise e


def run_vmr_temporal(bin_file, input_file, output_file, plot_file=None, exp_choice=None, type='experiment'):
    try:
        variables = vmr_get_variables(type=type, exp_choice=exp_choice)
        start_simulation(bin_file, input_file, output_file)
        vmr_start_controller(input_file, output_file, variables, type=type)

        time.sleep(5)
        if type == 'experiment':
            try:
                plot(output_file, plot_file)
            except Exception as e:
                print(f"Python: WARNING plot error: {str(e)}")

        input("Python: Press enter to finish")
        


    except KeyboardInterrupt:
        print('\nPython: Stopping due to KeyboardInterrupt')
    except Exception as e:
        print(f"Python error: {str(e)}")
        raise e


if __name__ == "__main__":
    run_make()
    subject_name = input("Nombre del sujeto: ")
    exp_choice = None
    type_choice = None

    choices = [
        "v",
        "vt",
        "f",
        "ft",
        "vft"
        ]

    # VMR o Fuerza
    while exp_choice not in choices:
        txt = [
            "Elegir tipo de simulación. (V, VT o F)",
            "v: vmr",
            "vt: vmr + temporal",
            "ft: fuerza + temporal",
            "vft: fuerza, vmr + temporal"
        ]
        print("\n".join(txt))
        exp_choice = input()


    # Demo o Experimento
    while type_choice not in ["d", "e"]:
        txt = [
            "Elegir tipo de simulación.(E o D)",
            "d: demo",
            "e: experimento"
        ]
        print("\n".join(txt))
        type_choice = input()
    type = 'demo' if type_choice == "d" else 'experiment'

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    data_path = os.path.join(sys.path[0], '../data')
    os.makedirs(data_path, exist_ok=True)

    filepreffix = f'{exp_choice}_{subject_name}_{type_choice}_{timestamp}'
    input_file = os.path.join(data_path, f'{filepreffix}_in.csv')
    output_file = os.path.join(data_path, f'{filepreffix}_out.csv')
    if type == 'experiment':
        plot_file = os.path.join(data_path, f'{filepreffix}_plot.png')
    else:
        plot_file = None

    if exp_choice == "v":
        bin_file = os.path.join(sys.path[0], '../bin/lin-x86_64/vmr')
        run(
            bin_file=bin_file,
            input_file=input_file,
            output_file=output_file,
            plot_file=plot_file,
            type=type
            )

    elif exp_choice == "vt":
        bin_file = os.path.join(sys.path[0], '../bin/lin-x86_64/vmr_temporal')
        run_vmr_temporal(
            bin_file=bin_file,
            input_file=input_file,
            output_file=output_file,
            plot_file=plot_file,
            exp_choice=exp_choice,
            type=type
            )

    elif exp_choice == "ft":
        bin_file = os.path.join(sys.path[0], '../bin/lin-x86_64/force_temporal')
        run_vmr_temporal(
            bin_file=bin_file,
            input_file=input_file,
            output_file=output_file,
            plot_file=plot_file,
            exp_choice=exp_choice,
            type=type
            ) 

    elif exp_choice == "vft":
        bin_file = os.path.join(sys.path[0], '../bin/lin-x86_64/vmr_force_temporal')
        run_vmr_temporal(
            bin_file=bin_file,
            input_file=input_file,
            output_file=output_file,
            plot_file=plot_file,
            exp_choice=exp_choice,
            type=type
            ) 

    zip_file = os.path.join(data_path, f"{filepreffix}.zip")
    # print(f"Python: compressing files into {zip_file}")
    # zipObj = ZipFile(zip_file, 'w')
    # for file in [input_file, output_file]:
    #     if os.path.exists(file):
    #         zipObj.write(file, os.path.basename(file))
    zipObj.close()
    for file in [input_file]:
        if os.path.exists(file):
            os.remove(file) 

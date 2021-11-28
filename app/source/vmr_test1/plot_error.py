import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy import trapz
import math
from scipy.spatial.transform import Rotation
from numpy.linalg import norm


def rotate_trial_data(trial_data, angle):
    theta = math.radians(angle)  # 0 es arriba en la sim
    axis = [0, 0, 1]  # z
    axis = axis / norm(axis)
    rot = Rotation.from_rotvec(theta * axis)
    trial_data['pos_rot'] = [rot.apply([x, y, z]) for x, y, z in zip(trial_data.x, trial_data.y, trial_data.z)]
    trial_data['x'] = [x for [x, y, z] in trial_data.pos_rot]
    trial_data['y'] = [y for [x, y, z] in trial_data.pos_rot]
    trial_data['z'] = [z for [x, y, z] in trial_data.pos_rot]
    trial_data.drop('pos_rot', axis=1, inplace=True)
    return trial_data


def calculate_error_area(trial_data, angle):
    trial_data = rotate_trial_data(trial_data, angle)
    x = [trial_data.iloc[0].x, trial_data.iloc[-1].x]
    y = [trial_data.iloc[0].y, trial_data.iloc[-1].y]
    coefficients = np.polyfit(x, y, 1)
    polynomial = np.poly1d(coefficients)
    error_curve = trial_data.y - polynomial(trial_data.x)
    area_error = trapz(error_curve, x=trial_data.x)
    area_error_abs = trapz(np.abs(error_curve), x=trial_data.x)
    return area_error, area_error_abs


if __name__ == "__main__":
    output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/out_20211022212151_ESTE.csv'
    names = ['trial', 'x', 'y', 'z']
    var_names = ['angle', 'vmr', 'blockN']
    names += var_names
    df = pd.read_csv(output_file, names=names, index_col=False)
    df['x'] = -df['x']*100
    df['y'] = df['y']*100
    block_count = len(df.blockN.unique())
    fig, axs = plt.subplots(3, block_count, sharey='row')
    fig.tight_layout()

    grouped = df.groupby(['trial', 'blockN', 'vmr'])

    for ax in axs[0]:
        ax.axis('equal')
        ax.set_box_aspect(1)

    for (trial, blockN, vmr), group in grouped:
        group.plot(x='y', y='x', ax=axs[0][blockN], label=f'trial {trial}', legend=False)

    for (blockN, vmr), group in df.groupby(['blockN', 'vmr']):
        trial_count = len(group.trial.unique())
        axs[0][blockN].set_title(f'vmr: {vmr} trials: {trial_count}')

    grouped_block = df.groupby(['blockN'])
    for blockN, group_block in grouped_block:
        grouped = group_block.groupby(['trial', 'blockN', 'vmr', 'angle'])
        area_error_arr = []
        area_error_abs_arr = []
        for (trial, blockN, vmr, angle), group in grouped:
            area_error, area_error_abs = calculate_error_area(group, angle)
            area_error_arr.append(area_error)
            area_error_abs_arr.append(area_error_abs)
        axs[1][blockN].plot(area_error_arr)
        axs[1][blockN].set_title('Error signado')
        axs[2][blockN].plot(area_error_abs_arr)
        axs[2][blockN].set_title('Error absoluto')

    plt.show()

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from .plot_error import calculate_error_area
from .distance import distance


# Trajectory
def plot_trajectory(df, vmr, blockN, trial_vars, axs, colors):
    # Plot aspect
    for ax in axs[0]:
        ax.axis('equal')
        ax.set_box_aspect(1)

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        group = filter_hold_time(group)
        group.plot(x='y', y='x', ax=axs[0][blockN], legend=False)

    trial_count = len(df.trial.unique())
    axs[0][blockN].set_title(f'vmr: {vmr} trials: {trial_count}', fontsize=8)

    # Line colors for trayectory
    for i, j in enumerate(axs[0][blockN].lines):
        j.set_color(colors[i])


# Area errors (integral)
def plot_area_errors(df, blockN, trial_vars, axs, colors):

    # Line colors for area error
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        group = filter_hold_time(group)
        area_error, area_error_abs = calculate_error_area(group, angle)
        axs[1][blockN].scatter(trial, area_error, s=5, color=colors[trial - min_trial])
        axs[2][blockN].scatter(trial, area_error_abs, s=5, color=colors[trial - min_trial])

    axs[1][blockN].set_title('Error de area signado', fontsize=8)
    axs[2][blockN].set_title('Error de area absoluto', fontsize=8)


# Distancia recorrida
def plot_curve_distance_and_velocity(df, blockN, trial_vars, axs, colors):

    # Line colors for curve distance
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        group = filter_hold_time(group)
        d = distance(group)
        dt = (group.timeMs.max() - group.timeMs.min())/1000
        axs[3][blockN].scatter(trial, d, s=5, color=colors[trial - min_trial])
        axs[4][blockN].scatter(trial, d/dt, s=5, color=colors[trial - min_trial])
    axs[3][blockN].set_title('Distancia recorrida [cm]', fontsize=8)
    axs[4][blockN].set_title('Velocidad media [cm/s]', fontsize=8)


def filter_hold_time(df, hold_time=500):
    filtered_df = df.copy()
    trial_time = filtered_df.timeMs.max() - hold_time
    filtered_df = filtered_df[filtered_df.timeMs < trial_time]
    return filtered_df


def plot(output_file):
    names = [
        'trial',
        'timeMs',
        'x', 'y', 'z',
        'angle',
        'vmr',
        'blockN',
        'trialSuccess'
        ]
    df = pd.read_csv(output_file, names=names, index_col=False)
    df['x'] = -df['x']*100
    df['y'] = df['y']*100

    # Prepare plots
    block_count = len(df.blockN.unique())
    fig, axs = plt.subplots(5, block_count, sharey='row')
    fig.tight_layout()

    for ax in axs.flat:
        plt.setp(ax.get_xticklabels(), fontsize=8)
        plt.setp(ax.get_yticklabels(), fontsize=8)

    # Prepare data
    trial_vars = ['trial', 'angle', 'trialSuccess']
    block_vars = ['vmr', 'blockN']
    grouped_block = df.groupby(block_vars)

    colormap = plt.cm.winter

    for (vmr, blockN), block_group in grouped_block:
        colors = [colormap(i) for i in np.linspace(0, 1, len(block_group.trial.unique()))]

        block_group = block_group[block_group.trialSuccess == 1]
        plot_trajectory(block_group, vmr, blockN, trial_vars, axs, colors)
        plot_area_errors(block_group, blockN, trial_vars, axs, colors)
        plot_curve_distance_and_velocity(block_group, blockN, trial_vars, axs, colors)

    plt.show()


if __name__ == "__main__":
    # Read file
    output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/vmr_Nico_2021_11_09_22_07_35_out.csv'
    # output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/vmr_Carolina_2021_11_09_19_28_24_out.csv'
    plot(output_file)

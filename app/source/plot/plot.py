import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from .plot_error import calculate_error_area
from .distance import distance


# Trajectory
def plot_trajectory(df, vmr, blockN, trial_vars, axs, colors, df_summary):
    # Plot aspect
    for ax in axs[0]:
        ax.axis('equal')
        ax.set_box_aspect(1)

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        if df_summary is not None:
            group = filter_outside_beeps(group, df_summary, trial)
        else: 
            group = filter_hold_time(group)
        group.plot(x='y', y='x', ax=axs[0][blockN], legend=False)

    trial_count = len(df.trial.unique())
    axs[0][blockN].set_title(f'vmr: {vmr} trials: {trial_count}', fontsize=5)

    # Line colors for trayectory
    for i, j in enumerate(axs[0][blockN].lines):
        j.set_color(colors[i])


# Area errors (integral)
def plot_area_errors(df, blockN, trial_vars, axs, colors, df_summary):

    # Line colors for area error
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        if df_summary is not None:
            group = filter_outside_beeps(group, df_summary, trial)
        else: 
            group = filter_hold_time(group)
        area_error, area_error_abs = calculate_error_area(group, angle)
        axs[1][blockN].scatter(trial, area_error, s=2, color=colors[trial - min_trial])
        axs[2][blockN].scatter(trial, area_error_abs, s=2, color=colors[trial - min_trial])

    axs[1][blockN].set_title('Error de area signado', fontsize=5)
    axs[2][blockN].set_title('Error de area absoluto', fontsize=5)


# Distancia recorrida
def plot_curve_distance_and_velocity(df, blockN, trial_vars, axs, colors, df_summary):

    # Line colors for curve distance
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        if df_summary is not None:
            group = filter_outside_beeps(group, df_summary, trial)
        else: 
            group = filter_hold_time(group)
        d = distance(group)
        dt = (group.timeMs.max() - group.timeMs.min())/1000
        axs[3][blockN].scatter(trial, d, s=2, color=colors[trial - min_trial])
        axs[4][blockN].scatter(trial, d/dt, s=2, color=colors[trial - min_trial])
    axs[3][blockN].set_title('Distancia recorrida [cm]', fontsize=5)
    axs[4][blockN].set_title('Velocidad media [cm/s]', fontsize=5)

def plot_temporal_error(df_summary, df, blockN, trial_vars, axs, colors):
    # Line colors
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        trial_data = df_summary[df_summary.trial == trial]
        first_beep = trial_data.first_beep
        second_beep = trial_data.second_beep
        period = trial_data.period
        temp_error = (second_beep - first_beep) - period
        axs[5][blockN].scatter(trial, temp_error, s=2, color=colors[trial - min_trial])
    axs[5][blockN].set_title('Error temporal [ms]', fontsize=5)



def filter_hold_time(df, hold_time=500):
    filtered_df = df.copy()
    trial_time = filtered_df.timeMs.max() - hold_time
    filtered_df = filtered_df[filtered_df.timeMs < trial_time]
    return filtered_df

def filter_outside_beeps(df, df_summary, trial):
    # Keep only time between beeps
    first_beep = float(df_summary.loc[df_summary.trial == trial, "first_beep"])
    second_beep = float(df_summary.loc[df_summary.trial == trial, "second_beep"])
    df.drop(df[df['timeMs'] < first_beep].index, inplace = True)
    df.drop(df[df['timeMs'] > second_beep].index, inplace = True)
    return df

def plot(output_file, plot_file=None, names=None, file_summary=None):
    if not names:
        if len(pd.read_csv(output_file).columns) == 9:
            names = [
                'trial',
                'timeMs',
                'x', 'y', 'z',  # [m]
                'angle',
                'vmr',
                'blockN',
                'trialSuccess'
            ]
        elif len(pd.read_csv(output_file).columns) == 11:
            names = [
                'trial',
                'timeMs',
                'x', 'y', 'z',  # [m]
                'angle',
                'vmr',
                'blockN',
                'sound', 
                'force_type',
                'trialSuccess'
            ]
        elif len(pd.read_csv(output_file).columns) == 14:
            names = [
                'trial',
                'timeMs',
                'x', 'y', 'z',  # [m]
                'fx', 'fy', 'fz',  
                'angle',
                'vmr',
                'blockN',
                'sound', 
                'force_type',
                'trialSuccess'
            ]
        else:
            raise Exception('Columns in plot are not well defined')
    df = pd.read_csv(output_file, names=names, index_col=False)
    df['x'] = -df['x']*100  # [cm]
    df['y'] = df['y']*100   # [cm]

    if file_summary:
        columns_summary = [
            'trial',
            'first_beep',
            'second_beep',
            'period',
            'angle',
            'vmr',
            'blockN',
            'sound', 
            'force_type',
            'trialSuccess'
        ]
        df_summary = pd.read_csv(file_summary, names=columns_summary, index_col=False)
    else:
        df_summary = None

    # Prepare plots
    block_count = len(df.blockN.unique())

    if file_summary: 
        metrics_count = 6
    else:
        metrics_count = 5

    fig, axs = plt.subplots(metrics_count, block_count, sharey='row')
    fig.tight_layout()

    for ax in axs.flat:
        plt.setp(ax.get_xticklabels(), fontsize=5)
        plt.setp(ax.get_yticklabels(), fontsize=5)

    # Prepare data
    trial_vars = ['trial', 'angle', 'trialSuccess']
    block_vars = ['vmr', 'blockN']
    grouped_block = df.groupby(block_vars)

    colormap = plt.cm.winter

    for (vmr, blockN), block_group in grouped_block:
        colors = [colormap(i) for i in np.linspace(0, 1, len(block_group.trial.unique()))]

        block_group = block_group[block_group.trialSuccess == 1]
        plot_trajectory(block_group, vmr, blockN, trial_vars, axs, colors, df_summary)
        plot_area_errors(block_group, blockN, trial_vars, axs, colors, df_summary)
        plot_curve_distance_and_velocity(block_group, blockN, trial_vars, axs, colors, df_summary)
        if file_summary: 
            plot_temporal_error(df_summary, block_group, blockN, trial_vars, axs, colors, )

    if plot_file:
        print(f"Saving plot to {plot_file}")
        plt.savefig(f'{plot_file}', dpi=500)
    else:
        print("Showing plot")
        plt.show()


   
if __name__ == "__main__":
    # Read file
    output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/vmr_Nico_2021_11_09_22_07_35_out.csv'
    # output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/vmr_Carolina_2021_11_09_19_28_24_out.csv'
    plot(output_file)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from .plot_error import calculate_error_area
from .distance import distance


# Trajectory
def plot_trajectory(df, vmr, blockN, trial_vars, ax, colors, df_summary, fontsize=5, blockName=None, force_type=None):
    # Plot aspect
    ax.axis('equal')
    ax.set_box_aspect(1)

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        if df_summary is not None:
            group = filter_outside_beeps(group, df_summary, trial)
        else: 
            group = filter_hold_time(group)
        group.plot(x='y', y='x', ax=ax, legend=False)

    trial_count = len(df.trial.unique())
    if blockName and force_type:
        ax.set_title(f"{blockName} fuerza {force_type}", fontsize=fontsize)
    elif blockName:
        ax.set_title(blockName, fontsize=fontsize)
    else:
        ax.set_title(f'vmr: {vmr} trials: {trial_count}', fontsize=fontsize)
    ax.set_xlabel('y', fontsize=fontsize)
    ax.set_ylabel('x', fontsize=fontsize)

    # Line colors for trayectory
    for i, j in enumerate(ax.lines):
        j.set_color(colors[i])


# Area errors (integral)
def plot_area_errors(df, blockN, trial_vars, ax_err, ax_err_abs, colors, df_summary, fontsize=5):

    # Line colors for area error
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        if df_summary is not None:
            group = filter_outside_beeps(group, df_summary, trial)
        else: 
            group = filter_hold_time(group)
        area_error, area_error_abs = calculate_error_area(group, angle)
        ax_err.scatter(trial, area_error, s=2, color=colors[trial - min_trial])
        ax_err_abs.scatter(trial, area_error_abs, s=2, color=colors[trial - min_trial])
            
  
    ax_err.set_ylabel('Error de area signado', fontsize=fontsize)
    ax_err.set_xlabel('numero de trial', fontsize=fontsize)
    ax_err_abs.set_ylabel('Error de area absoluto', fontsize=fontsize)
    ax_err_abs.set_xlabel('numero de trial', fontsize=fontsize)


# Distancia recorrida
def plot_curve_distance_and_velocity(df, blockN, trial_vars, ax_d, ax_v, colors, df_summary, fontsize=5):

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
        ax_d.scatter(trial, d, s=2, color=colors[trial - min_trial])
        ax_v.scatter(trial, d/dt, s=2, color=colors[trial - min_trial])
    ax_d.set_ylabel('Distancia recorrida [cm]', fontsize=fontsize)
    ax_d.set_xlabel('numero de trial', fontsize=fontsize)
    ax_v.set_ylabel('Velocidad media [cm/s]', fontsize=fontsize)
    ax_v.set_xlabel('numero de trial', fontsize=fontsize)

def plot_temporal_error(df_summary, df, blockN, trial_vars, ax, colors, fontsize=5):
    # Line colors
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        trial_data = df_summary[df_summary.trial == trial]
        first_beep = trial_data.first_beep
        second_beep = trial_data.second_beep
        period = trial_data.period
        temp_error = (second_beep - first_beep) - period
        ax.scatter(trial, temp_error, s=2, color=colors[trial - min_trial])
    ax.set_ylabel('Error temporal [ms]', fontsize=fontsize)
    ax.set_xlabel('numero de trial', fontsize=fontsize)

def plot_rapidez(df_summary, df, blockN, trial_vars, ax, fig, colors, fontsize=5):
    fig.suptitle('Rapidez (por ms) [cm/s]')
    print(f"plot_rapidez({blockN}, {trial_vars})")
    # For line colors
    min_trial = df.trial.min()

    grouped_trial = df.groupby(trial_vars)
    for (trial, angle, trialSuccess), group in grouped_trial:
        group = filter_outside_beeps(group, df_summary, trial)
        group["timeMsAbs"] = group.timeMs - group.timeMs.min()
        bucket_size = 5 # ms
        group["timeMsAbsBucket"] = (group.timeMsAbs // bucket_size).astype(int)
        grouped_ms = group.groupby("timeMsAbsBucket")
        time = []
        v = []
        for (timeMsAbsBucket), group_ms in grouped_ms:
            d = distance(group_ms)
            dt = (group_ms.timeMsAbs.max() - group_ms.timeMsAbs.min())/1000
            if dt != 0:
                time += [timeMsAbsBucket * bucket_size]
                v += [d/dt]
        ax.scatter(time, v, s=1, color=colors[trial - min_trial], alpha=0.25)
    # ax.set_title('Rapidez (por ms) [cm/s]', fontsize=fontsize)
     

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

def plot(output_file, plot_file=None, names=None, file_summary=None, fontsize=5, figsize=None, subplot_params={}, plot_rapidez=False, block_filter=None, blockNames=None, plot_trayect=True, plot_area_err=True, plot_d_and_vel=True, plot_temp_err=True):
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

    # Filter blocks
    if block_filter:
        df = df[df.blockN.isin(block_filter)]
        if file_summary:
            df_summary = df_summary[df_summary.blockN.isin(block_filter)]
    

    # Prepare plots
    block_count = len(df.blockN.unique())
    metrics_count = 0
    if plot_trayect:
        metrics_count +=1
    if plot_area_err:
        metrics_count +=2
    if plot_d_and_vel:
        metrics_count +=2
    if file_summary: 
        if plot_temp_err:
            metrics_count += 1
        if plot_rapidez:
            fig2, axs2 = plt.subplots(block_count, 1, sharex='col', sharey='col', figsize=figsize)


    fig, axs = plt.subplots(metrics_count, block_count, sharey='row', **subplot_params)
    fig.tight_layout()

    for ax in axs.flat:
        plt.setp(ax.get_xticklabels(), fontsize=fontsize)
        plt.setp(ax.get_yticklabels(), fontsize=fontsize)




    # Prepare data
    trial_vars = ['trial', 'angle', 'trialSuccess']
    block_vars = ['blockN', 'vmr']
    grouped_block = df.sort_values('blockN').groupby(block_vars)

    colormap = plt.cm.winter
    blockN_list = list(df.blockN.unique())
    blockN_list.sort()

    
    for (blockN, vmr), block_group in grouped_block:
        
        subplot_i = blockN_list.index(blockN)
        colors = [colormap(i) for i in np.linspace(0, 1, len(block_group.trial.unique()))]
        if 'force_type' in names:
            force_type = block_group.force_type.unique()[0]
        else:
            force_type = None

        if blockNames:
            blockName=blockNames[subplot_i]
        else:
            blockName=None

        block_group = block_group[block_group.trialSuccess == 1]


        axs_offset = 0
        if plot_trayect:
            if block_count==1:
                ax = axs[0]
            else:
                ax = axs[0][subplot_i]
            plot_trajectory(block_group, vmr, blockN, trial_vars, ax, colors, df_summary, fontsize=fontsize, blockName=blockName, force_type=force_type)
        else:
            axs_offset +=1

        if plot_area_err:
            if block_count==1:
                ax_err, ax_err_abs = axs[1-axs_offset], axs[2-axs_offset]
            else:
                ax_err, ax_err_abs = axs[1-axs_offset][subplot_i], axs[2-axs_offset][subplot_i]
            plot_area_errors(block_group, blockN, trial_vars, ax_err, ax_err_abs , colors, df_summary, fontsize=fontsize)
        else:
            axs_offset +=2

        if plot_d_and_vel:
            if block_count==1:
                ax_d, ax_v = axs[3-axs_offset], axs[4-axs_offset]
            else:
                ax_d, ax_v = axs[3-axs_offset][subplot_i], axs[4-axs_offset][subplot_i]
            plot_curve_distance_and_velocity(block_group, blockN, trial_vars, ax_d, ax_v, colors, df_summary, fontsize=fontsize)
        else:
            axs_offset +=2
        
        if file_summary:
            if plot_temp_err: 
                if block_count==1:
                    ax = axs[5-axs_offset]
                else:
                    ax = axs[5-axs_offset][subplot_i]
                plot_temporal_error(df_summary, block_group, blockN, trial_vars, ax, colors, fontsize=fontsize)
            if plot_rapidez:
                print("Start plot_rapidez")
                if block_count==1:
                    ax2 = axs2
                else:
                    ax2 = axs2[subplot_i]
                plot_rapidez(df_summary, block_group, blockN, trial_vars, ax2, fig2, colors,fontsize=fontsize)
                fig2.savefig(plot_file.replace(".png", "-rapidez.png"), dpi=500)
        


    if plot_file:
        print(f"Saving plot to {plot_file}")
        fig.savefig(f'{plot_file}', dpi=500)
        if file_summary and plot_rapidez:
            fig2.savefig(plot_file.replace(".png", "-rapidez.png"), dpi=500)
    else:
        print("Showing plot")
        fig.show()
        


   
if __name__ == "__main__":
    # Read file
    output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/vmr_Nico_2021_11_09_22_07_35_out.csv'
    # output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/vmr_Carolina_2021_11_09_19_28_24_out.csv'
    plot(output_file)

import os
# from turtle import color 
import pandas as pd
import matplotlib.pyplot as plt
from analisis_datos import * 
import numpy as np

from plot.plot_error import rotate_trial_data
from scipy import stats
from matplotlib.cbook import boxplot_stats
import seaborn as sns
import matplotlib.patches as mpatches
import random
from statsmodels.stats.multitest import fdrcorrection
from plot.plot import distance
from plot.distance import total_distance_vect
import time
from scipy import signal
from matplotlib.gridspec import GridSpec

start_time = time.time()
last_time = start_time
print("Comienzo generacion imagenes")



file= os.path.join(path, "Merge_analisis.csv")
df = pd.read_csv(file, index_col=False)
df = df[df.trialSuccess == 1]

df.drop(df[df.sujeto=='vft_caro'].index, inplace = True)

block_vars = ['blockName']
metrics = [
    'area_error',
    'area_error_abs',
    'd',
    'temporal_error',
    'velocidad_media'
]
df['velocidad_media'] = df['d'] / df['reproduced_period']
df['temporal_error_abs'] = df['temporal_error'].abs()

# Agregar offset segun el tipo de trial (vmr, vmr aftereffects, etc) para generar el eje x
blockNamesOffset = {
    "Adaptacion": 0,
    "VMR": 30,
    "VMR-AfterEffects": 60,
    "Force": 90,
    "Force-AfterEffects": 120,
}
for blockName in df.blockName.unique():
    offset = blockNamesOffset[blockName]
    df.loc[df.blockName == blockName, "x_axis"] = df.loc[df.blockName == blockName, "blockTrialSuccessN"] + offset 

df.x_axis = df.x_axis.astype(int)

def plot_stats(title, last_time):
    t1 = last_time
    t2 = time.time()
    dt = t2-t1
    print(f"Finalizado grafico: {title} ({round(dt//60)}m{round(dt%60)}s)")
    return t2

def create_axs(row_size=1, col_size=1, sharex=False, sharey=False, figsize=None):
    fig, axs = plt.subplots(row_size, col_size, sharex=sharex, sharey=sharey, constrained_layout=True, figsize=figsize)
    if row_size*col_size == 1:
        return fig, axs

    for ax in axs.flat:
            plt.setp(ax.get_xticklabels(), fontsize=10)
            plt.setp(ax.get_yticklabels(), fontsize=10)
    return fig, axs


def read_file_for_sujeto(sujeto, columns):
    file = files_dict[sujeto]["file"]
    file_path = os.path.join(path, files_dict[sujeto]["path"])
    file = os.path.join(file_path, file)
    df_sujeto = pd.read_csv(file, names=columns, index_col=False)
    # Fix coordinates (x to -x & *100)
    df_sujeto['x'] = -df_sujeto['x']*100  # [cm]
    df_sujeto['y'] = df_sujeto['y']*100   # [cm]

    return df_sujeto

def plot_trayectoria_sujeto(df, df_summary, title):
    fig, axs = create_axs(col_size=len(df_summary.blockName.unique()), sharey='row')
    fig.suptitle(title)
    for ax in axs:
        ax.axis('equal')
        ax.set_box_aspect(1)
    colormap = plt.cm.winter
    colors = [colormap(i) for i in np.linspace(0, 1, len(df_summary.blockTrialSuccessN.unique()))]
    grouped_block = df.groupby("blockN")
    for blockN, block_group in grouped_block:
        ax = axs[blockN]
        blockName = df_summary[df_summary.blockN == blockN].blockName.unique()[0]

        block_group = block_group[block_group.trialSuccess == 1]
        grouped_trial = block_group.groupby('trial')
        for trial, group in grouped_trial:
            # Keep only time between beeps
            first_beep = float(df_summary.loc[df_summary.trial == trial, "first_beep"])
            second_beep = float(df_summary.loc[df_summary.trial == trial, "second_beep"])
            group.drop(group[group['timeMs'] < first_beep].index, inplace = True)
            group.drop(group[group['timeMs'] > second_beep].index, inplace = True)

            # Plot
            group.plot(x='y', y='x', ax=ax, legend=False)
        # Line colors for trayectory
        for i, j in enumerate(ax.lines):
            j.set_color(colors[i])
        ax.set_title(blockName, fontsize=10)
        ax.set_xlabel('x', fontsize=10)
        ax.set_ylabel('y', fontsize=10)
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)

def plot_errores_sujeto(df_summary, title):
    metrics = [
        'area_error',
        'area_error_abs',
        'temporal_error',
    ]
    fig, axs = create_axs(row_size=len(metrics), col_size=len(df_summary.blockName.unique()), sharey='row')
    fig.suptitle(title)
    colormap = plt.cm.winter
    colors = [colormap(i) for i in np.linspace(0, 1, len(df_summary.blockTrialSuccessN.unique()))]
    grouped_block = df_summary.groupby(["blockName", "blockN"])
    for (blockName, blockN), block_group in grouped_block:
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i][blockN]
            ax.set_title(blockName, fontsize=10)
            ax.set_xlabel('numero de trial', fontsize=10)
            ax.set_ylabel(metric.replace("_", " "), fontsize=10)
            ax.scatter(block_group.blockTrialSuccessN, block_group[metric], c=colors, s=2)
            subplot_i += 1
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)

def plot_pendiente_y_mediana_sujeto(df_summary, title):
    metrics = [
        'area_error_abs',
        'temporal_error_abs',
    ]
    fig, axs = create_axs(row_size=len(metrics), col_size=len(df_summary.blockName.unique()), sharey='row', sharex='col')
    fig.suptitle(title)
    colormap = plt.cm.winter
    colors = [colormap(i) for i in np.linspace(0, 1, len(df_summary.blockTrialSuccessN.unique()))]
    grouped_block = df_summary.groupby(["blockName", "blockN"])
    for (blockName, blockN), block_group in grouped_block:
        subplot_i = 0
        first_half = block_group[block_group['blockTrialSuccessN'] <= 15]
        last_half = block_group[block_group['blockTrialSuccessN'] > 15]
        for metric in metrics:
            # Errores
            ax = axs[subplot_i]
            ax.set_title(blockName, fontsize=10)
            ax.set_xlabel('numero de trial', fontsize=10)
            ax.set_ylabel(metric.replace("_", " "), fontsize=10)
            ax.scatter(block_group.blockTrialSuccessN, block_group[metric], c=colors, s=2)
            # Slope & median
            # slope_robust, intercept = stats.siegelslopes(first_half['blockTrialSuccessN'], first_half[metric])
            slope, intercept, r_value, p_value, std_err = stats.linregress(first_half['blockTrialSuccessN'], first_half[metric])
            ax.plot(first_half.blockTrialSuccessN, intercept + slope * first_half.blockTrialSuccessN, color='red', label="Pendiente primera mitad")
            median_last_half = last_half[metric].median() 
            ax.plot(last_half.blockTrialSuccessN, [median_last_half]*len(last_half), color='blue', label="Mediana segunda mitad")
            ax.legend(loc="upper right", fontsize=10)
            subplot_i += 1
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)  


def plot_boxplot_pendiente_y_mediana(df, title):
    metrics = [
    'area_error_abs',
    'temporal_error_abs',
    ]   
    fig, axs = create_axs(row_size=2, col_size=len(metrics))
    fig.suptitle(title)
    
    new_df = pd.DataFrame(columns = ['sujeto', 'blockName', 'metric', 'slope', 'median_last_half'])
    grouped_blockName = df[df.blockName.isin(["Force", "VMR"])].groupby("blockName")
    for blockName, group_blockName in grouped_blockName:

        grouped_sujeto = group_blockName.groupby("sujeto")
        for sujeto, group_sujeto  in grouped_sujeto:
            first_half = group_sujeto[group_sujeto['blockTrialSuccessN'] <= 15]
            last_half = group_sujeto[group_sujeto['blockTrialSuccessN'] > 15]
            for metric in metrics:
                slope, intercept, r_value, p_value, std_err = stats.linregress(first_half['blockTrialSuccessN'], first_half[metric])
                median_last_half = last_half[metric].median() 
                new_df.loc[len(new_df.index)] = [sujeto, blockName, metric, slope, median_last_half]           
    outliers_dict = {}
    for blockName in new_df['blockName'].unique():
        outliers_dict[blockName] = []
    subplot_row = 0
    for metric in metrics:
        ax1 = axs[0][subplot_row]
        ax2 = axs[1][subplot_row]

        subplot_row += 1
        data = new_df[new_df.metric == metric].copy()
        sns.boxplot(ax=ax1, x="blockName",y="slope",data=data, whis=1.5)
        sns.swarmplot(ax=ax1, x="blockName",y="slope",data=data, color=".25")
        ax1.set_ylabel(f"{metric.replace('_', ' ')}\npendiente", fontsize=10, rotation='vertical', ha='center')
        ax1.set_xlabel("", fontsize=10)
        sns.boxplot(ax=ax2, x="blockName",y="median_last_half",data=data, whis=1.5)
        sns.swarmplot(ax=ax2, x="blockName",y="median_last_half",data=data, color=".25")
        ax2.set_ylabel(f"{metric.replace('_', ' ')}\nmediana", fontsize=10, rotation='vertical', ha='center')
        ax2.set_xlabel("", fontsize=10)

        blockName_i = 0
        for blockName in data['blockName'].unique():
        
            outliers_df = pd.DataFrame()
            outliers = boxplot_stats(data[data['blockName'] == blockName]['slope'], whis=1.5)[0]['fliers']
            median = boxplot_stats(data[data['blockName'] == blockName]['slope'], whis=1.5)[0]['med']
            for outlier in outliers:
                if outlier > median:
                    outliers_df = outliers_df.append(data[(data['blockName'] == blockName) & (data['slope'] == outlier)])
            for row in outliers_df.iterrows():
                sujeto = row[1]['sujeto']
                ax1.annotate(sujeto, xy=(blockName_i, row[1]['slope']), xytext=(2,0), textcoords='offset points', fontsize=10)
                outliers_dict[blockName] += [sujeto]

            outliers_df = pd.DataFrame()
            outliers = boxplot_stats(data[data['blockName'] == blockName]['median_last_half'], whis=1.5)[0]['fliers']
            median = boxplot_stats(data[data['blockName'] == blockName]['median_last_half'], whis=1.5)[0]['med']
            for outlier in outliers:
                if outlier > median:
                    outliers_df = outliers_df.append(data[(data['blockName'] == blockName) & (data['median_last_half'] == outlier)])
            for row in outliers_df.iterrows():
                sujeto = row[1]['sujeto']
                ax2.annotate(sujeto, xy=(blockName_i, row[1]['median_last_half']), xytext=(2,0), textcoords='offset points', fontsize=5)
                outliers_dict[blockName] += [sujeto]
            blockName_i += 1

    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)
    return outliers_dict

def sacar_outliers(df, outliers_dict):
    df_new = df.copy()
    outliers_vmr = outliers_dict['VMR']
    outliers_force = outliers_dict['Force']
    df_new['outlier_vmr'] = df_new.sujeto.isin(outliers_vmr)
    df_new['outlier_force'] = df_new.sujeto.isin(outliers_force)

    df_sin_outliers = df_new[
        ~(df_new.outlier_vmr & df_new.outlier_force) &
        ~(df_new.outlier_vmr & df_new.blockName.isin(['VMR', 'VMR-AfterEffects'])) &
        ~(df_new.outlier_force & df_new.blockName.isin(['Force', 'Force-AfterEffects']))
    ]
    len_outliers = len(outliers_vmr) + len(outliers_force)
    return df_sin_outliers, len_outliers

def plot_mediana(df_summary, title, fig, axs, metrics, color=None, show_text=True, text_offset=0, global_text_color=None, blockName_key="blockName"):
    fig.suptitle(title)
    params = {}
    if color:
        params["color"] = color    
    grouped_block = df_summary.groupby([blockName_key])
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i]
            median_series = median_df[metric]
            line, = ax.plot(median_df.index, median_series, **params)
            # Nombres de los bloques en el grafico
            if show_text:
                x_text = np.mean(median_df.index)
                max_y = df_summary.groupby("x_axis").median()[metric].max()
                min_y = df_summary.groupby("x_axis").median()[metric].min()
                y_text = max_y + (max_y - min_y) * text_offset
                if global_text_color:
                    text_color = global_text_color
                else:
                    text_color = line.get_color()
                ax.text(x_text, y_text, blockName, horizontalalignment='center', verticalalignment='top', fontsize=10, color=text_color)
            ax.set_xlabel('numero de trial', fontsize=10)
            ax.set_ylabel(metric.replace("_", " "), fontsize=10)            
            subplot_i += 1
    


    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)


def plot_banda_mad(df_summary, title, fig, axs, metrics, color=None):
    fig.suptitle(title)
    params = {}
    # if color:
    #     params["color"] = color    
    grouped_block = df_summary.groupby(["blockName"])
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        mad_df = block_group.groupby("x_axis").mad()
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i]
            median_series = median_df[metric]
            mad_series = mad_df[metric]
            ax.fill_between(x=median_df.index,
                        y1=median_series - mad_series,
                        y2=median_series + mad_series,
                        alpha=0.25,
                        **params
                        )      
            subplot_i += 1
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)

def plot_banda_sem_median(df_summary, title, fig, axs, metrics, color=None):
    fig.suptitle(title)
    params = {}
    if color:
        params["color"] = color    
    grouped_block = df_summary.groupby(["blockName"])
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        sem_df = block_group.groupby("x_axis").sem() * 1.25
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i]
            median_series = median_df[metric]
            sem_series = sem_df[metric]
            ax.fill_between(x=median_df.index,
                        y1=median_series - sem_series,
                        y2=median_series + sem_series,
                        alpha=0.25,
                        **params
                        )      
            subplot_i += 1
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500) 

def plot_promedio(df_summary, title, fig, axs, metrics, color=None, text_offset=0):
    fig.suptitle(title)
    params = {}
    # if color:
    #     params["color"] = color    
    grouped_block = df_summary.groupby(["blockName"])
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i]
            mean_series = mean_df[metric]
            line, = ax.plot(mean_df.index, mean_series, **params)
            # Nombres de los bloques en el grafico
            x_text = np.mean(mean_df.index)
            max_y = df_summary.groupby("x_axis").mean()[metric].max()
            min_y = df_summary.groupby("x_axis").mean()[metric].min()
            y_text = max_y + (max_y - min_y) * text_offset
            ax.text(x_text, y_text, blockName, horizontalalignment='center', verticalalignment='top', fontsize=10, color=line.get_color())
            ax.set_xlabel('numero de trial', fontsize=10)
            ax.set_ylabel(metric.replace("_", " "), fontsize=10)            
            subplot_i += 1

    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)   

def plot_banda_sem(df_summary, title, fig, axs, metrics, color=None):
    fig.suptitle(title)
    params = {}
    # if color:
    #     params["color"] = color    
    grouped_block = df_summary.groupby(["blockName"])
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        sem_df = block_group.groupby("x_axis").sem()
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i]
            mean_series = mean_df[metric]
            sem_series = sem_df[metric]
            ax.fill_between(x=mean_df.index,
                        y1=mean_series - sem_series,
                        y2=mean_series + sem_series,
                        alpha=0.25,
                        **params
                        )      
            subplot_i += 1
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500) 

def plot_comparacion_condiciones(df_summary, title, metrics):
    sujetos_vmr_primero = df_summary[(df_summary['trialSuccessN']==df_summary['x_axis']) & (df_summary['vmr']==1)].sujeto.unique()
    df_sujetos_vmr_primero = df_summary[df_summary.sujeto.isin(sujetos_vmr_primero)]
    len_sujetos_vmr_primero = len(df_sujetos_vmr_primero.sujeto.unique())
    sujetos_force_primero = df_summary[(df_summary['trialSuccessN']!=df_summary['x_axis']) & (df_summary['vmr']==1)].sujeto.unique()
    df_sujetos_force_primero = df_summary[df_summary.sujeto.isin(sujetos_force_primero)]
    len_sujetos_force_primero = len(df_sujetos_force_primero.sujeto.unique())
    fig, axs = create_axs(row_size=len(metrics), sharex='all', figsize=[6.4, 6.4*1.5])

    # Labels globales
    red_patch = mpatches.Patch(color='red', label=f"sujetos fuerza primero ({len_sujetos_force_primero})")
    blue_patch = mpatches.Patch(color='blue', label=f"sujetos vmr primero ({len_sujetos_vmr_primero})")
    for ax in axs:
        ax.legend(handles=[red_patch, blue_patch], loc='best', fontsize=5)    

    # Datos
    plot_mediana(df_sujetos_force_primero, title, fig, axs, metrics, show_text=False, color="red")
    plot_banda_sem_median(df_sujetos_force_primero, title, fig, axs, metrics, color="red")
    plot_mediana(df_sujetos_vmr_primero, title, fig, axs, metrics, show_text=True, global_text_color='black', color="blue")
    plot_banda_sem_median(df_sujetos_vmr_primero, title, fig, axs, metrics, color="blue")

def get_df_perturbacion(df_summary, outliers_dict, perturbacion, trials_adaptacion=10):
    # Drop outliers y otros bloques
    outliers = outliers_dict[perturbacion]
    df = df_summary.copy()
    sujetos = [sujeto for sujeto in df.sujeto.unique() if sujeto not in outliers]

    indices_to_drop = []
    indices_to_drop += list(df[df.sujeto.isin(outliers)].index)

    for sujeto in sujetos:
        df_sujeto = df_summary[df_summary.sujeto == sujeto]
        blockN_perturbacion, = df_sujeto[df_sujeto.blockName == perturbacion].blockN.unique()
        adaptacion, = df_sujeto[df_sujeto.blockN == blockN_perturbacion-1].blockName.unique()
        aftereffects, = df_sujeto[df_sujeto.blockN == blockN_perturbacion+1].blockName.unique()
        
        df_sujeto_bloques_to_drop = df_sujeto[~(df_sujeto.blockName.isin([adaptacion, perturbacion, aftereffects]))]
        indices_to_drop += list(df_sujeto_bloques_to_drop.index)

        df_sujeto_adaptacion_to_drop = df_sujeto[(df_sujeto.blockName == adaptacion) & (df_sujeto.blockTrialSuccessN < (30-trials_adaptacion))]
        indices_to_drop += list(df_sujeto_adaptacion_to_drop.index)

        df.loc[(df.sujeto==sujeto) & (df.blockName == adaptacion), 'bloque_efectivo'] = 'adaptacion'
        df.loc[(df.sujeto==sujeto) & (df.blockName == perturbacion), 'bloque_efectivo'] = 'perturbacion'
        df.loc[(df.sujeto==sujeto) & (df.blockName == aftereffects), 'bloque_efectivo'] = 'aftereffects'


    df = df.drop(indices_to_drop)

    # Redefine x_axis
    bloque_efectivo_offset = {
        'adaptacion': -(30-trials_adaptacion),
        'perturbacion': trials_adaptacion,
        'aftereffects': trials_adaptacion+30,
    }
    for bloque_efectivo in df.bloque_efectivo.unique():
        offset = bloque_efectivo_offset[bloque_efectivo]
        df.loc[df.bloque_efectivo == bloque_efectivo, "x_axis"] = df.loc[df.bloque_efectivo == bloque_efectivo, "blockTrialSuccessN"] + offset 
    df.x_axis = df.x_axis.astype(int)

    return df
        




'''
1. Imagenes sujeto vmr primero
a. Grafico de las trayectorias del sujeto (adaptacion, perturbacion y after effects)
b. Grafico de los erroes temporales, de area signado y de area abs
'''
title = "1a.Trayectoria sujeto con vmr al comienzo"
sujeto = "vft_sebastian"
bloques = [
    'Adaptacion',
    'VMR',
    'VMR-AfterEffects'
]
df_sujeto_vmr = df[(df.sujeto == sujeto) & (df.blockName.isin(bloques))]
df_sujeto_vmr_full = read_file_for_sujeto(sujeto, columns)
df_sujeto_vmr_full = df_sujeto_vmr_full[df_sujeto_vmr_full.blockN.isin(df_sujeto_vmr.blockN.unique())]
plot_trayectoria_sujeto(df_sujeto_vmr_full, df_sujeto_vmr, title)
plt.close()
last_time = plot_stats(title, last_time)

title = "1b.Errores sujeto con vmr al comienzo"
plot_errores_sujeto(df_sujeto_vmr, title)
plt.close()
last_time = plot_stats(title, last_time)
'''
2. Imagenes sujeto fuerza primero
a. Grafico de las trayectorias del sujeto (adaptacion, perturbacion y after effects)
b. Grafico de los erroes temporales, de area signado y de area abs
'''
title = "2a.Trayectoria sujeto con fuerza al comienzo"
sujeto = "vft_hilariob"
bloques = [
    'Adaptacion',
    'Force',
    'Force-AfterEffects'
]
df_sujeto_force = df[(df.sujeto == sujeto) & (df.blockName.isin(bloques))]
df_sujeto_force_full = read_file_for_sujeto(sujeto, columns)
df_sujeto_force_full = df_sujeto_force_full[df_sujeto_force_full.blockN.isin(df_sujeto_force.blockN.unique())]
plot_trayectoria_sujeto(df_sujeto_force_full, df_sujeto_force, title=title)
plt.close()
last_time = plot_stats(title, last_time)
title = "2b.Errores sujeto con fuerza al comienzo"
plot_errores_sujeto(df_sujeto_force, title)
plt.close()
last_time = plot_stats(title, last_time)
'''
3a. Pendiente de la primer mitad y mediana de la segunda mitad visualizada en un sujeto con vmr
3b. Boxplot de todos los sujetos, para pendiente de la primer mitad y mediana de la segunda mitad
3c. Igual que 3b pero sin los outliers, numerado por iteracion
TODO: usar RLM https://www.statsmodels.org/dev/examples/notebooks/generated/robust_models_0.html


'''
title = "3a. Pendiente y mediana - criterios de outliers - ejemplo sujeto"
df_sujeto_vmr = df[(df.sujeto == sujeto) & (df.blockName == "VMR")]
plot_pendiente_y_mediana_sujeto(df_sujeto_vmr, title)
plt.close()
last_time = plot_stats(title, last_time)
title = "3b. Boxplot de pendiente y mediana"
outliers_dict = plot_boxplot_pendiente_y_mediana(df, title)
df_sin_outliers, len_outliers = sacar_outliers(df, outliers_dict)
plt.close()
last_time = plot_stats(title, last_time)

'''
4a. Errores - mediana y banda mad - sin outliers
4b. Errores - mediana y banda standard error median - sin outliers
4c. Errores - promedio y banda standard error mean - sin outliers
'''
metrics = [
    'area_error',
    'area_error_abs',
    'temporal_error',
]
# title = "4a. Errores - mediana y banda mad - sin outliers"
# fig, axs = create_axs(row_size=len(metrics), sharex='all')
# plot_mediana(df_sin_outliers, title, fig, axs, metrics)
# plot_banda_mad(df_sin_outliers, title, fig, axs, metrics)

title = "4b. Errores - mediana y banda standard error median - sin outliers"
fig, axs = create_axs(row_size=len(metrics), sharex='all')
plot_mediana(df_sin_outliers, title, fig, axs, metrics)
plot_banda_sem_median(df_sin_outliers, title, fig, axs, metrics)
plt.close()
last_time = plot_stats(title, last_time)
# title = "4c. Errores - promedio y banda standard error mean - sin outliers"
# fig, axs = create_axs(row_size=len(metrics), sharex='all')
# plot_promedio(df_sin_outliers, title, fig, axs, metrics)
# plot_banda_sem(df_sin_outliers, title, fig, axs, metrics)


'''
5. Comparacion de sujetos con condiciones contrabalanceadas - Errores
TODO: separar vmr y fuerza (usar los dfs de 7.)
'''
title = "5. Comparacion de sujetos con condiciones contrabalanceadas"
metrics = [
    'area_error',
    'area_error_abs',
    'temporal_error',
    'd',
    'velocidad_media'
]
plot_comparacion_condiciones(df_sin_outliers, title, metrics)
plt.close()
last_time = plot_stats(title, last_time)

'''
6a. Distancia, error temporal y velocidad - mediana y banda mad - sin outliers
6b. Distancia, error temporal y velocidad - mediana y banda standard error median - sin outliers
6c. Distancia, error temporal y velocidad - promedio y banda standard error mean - sin outliers
'''
metrics = [
    'd',
    'temporal_error',
    'velocidad_media'
]
# title = "6a. Distancia, error temporal y velocidad - mediana y banda mad - sin outliers"
# fig, axs = create_axs(row_size=len(metrics), sharex='all')
# plot_mediana(df_sin_outliers, title, fig, axs, metrics)
# plot_banda_mad(df_sin_outliers, title, fig, axs, metrics)

title = "6b. Distancia, error temporal y velocidad - mediana y banda standard error median - sin outliers"
fig, axs = create_axs(row_size=len(metrics), sharex='all')
plot_mediana(df_sin_outliers, title, fig, axs, metrics)
plot_banda_sem_median(df_sin_outliers, title, fig, axs, metrics)
plt.close()
last_time = plot_stats(title, last_time)
# title = "6c. Distancia, error temporal y velocidad - promedio y banda standard error mean - sin outliers"
# fig, axs = create_axs(row_size=len(metrics), sharex='all')
# plot_promedio(df_sin_outliers, title, fig, axs, metrics)
# plot_banda_sem(df_sin_outliers, title, fig, axs, metrics)

'''
7a. Comparacion entre fuerza y vmr (10 trials)
7b. Comparacion entre fuerza y vmr (15 trials)
# TODO num de trial dentro del bloque
'''
title = "7a. Comparacion entre fuerza y vmr (10 trials)"
df_vmr = get_df_perturbacion(df, outliers_dict, 'VMR', trials_adaptacion=10)
df_force = get_df_perturbacion(df, outliers_dict, 'Force', trials_adaptacion=10)

metrics = [
    'area_error',
    'area_error_abs',
    'temporal_error',
    'd',
    'velocidad_media'
]
fig, axs = create_axs(row_size=len(metrics), sharex='all', figsize=[6.4, 6.4*1.5])
# Labels globales
green_patch = mpatches.Patch(color='green', label=f"VMR")
purple_patch = mpatches.Patch(color='purple', label=f"Fuerza")
for ax in axs:
    ax.legend(handles=[green_patch, purple_patch], loc='best', fontsize=5)    

plot_mediana(df_vmr, title, fig, axs, metrics, show_text=True, global_text_color='black', color="green", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_vmr, title, fig, axs, metrics, color="green")
plot_mediana(df_force, title, fig, axs, metrics, show_text=False, color="purple", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_force, title, fig, axs, metrics, color="purple")
plt.close()
last_time = plot_stats(title, last_time)

title = "7b. Comparacion entre fuerza y vmr (15 trials)"
df_vmr = get_df_perturbacion(df, outliers_dict, 'VMR', trials_adaptacion=15)
df_force = get_df_perturbacion(df, outliers_dict, 'Force', trials_adaptacion=15)

metrics = [
    'area_error',
    'area_error_abs',
    'temporal_error',
    'd',
    'velocidad_media'
]
fig, axs = create_axs(row_size=len(metrics), sharex='all', figsize=[6.4, 6.4*1.5])
# Labels globales
green_patch = mpatches.Patch(color='green', label=f"VMR")
purple_patch = mpatches.Patch(color='purple', label=f"Fuerza")
for ax in axs:
    ax.legend(handles=[green_patch, purple_patch], loc='best', fontsize=5)    

plot_mediana(df_vmr, title, fig, axs, metrics, show_text=True, global_text_color='black', color="green", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_vmr, title, fig, axs, metrics, color="green")
plot_mediana(df_force, title, fig, axs, metrics, show_text=False, color="purple", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_force, title, fig, axs, metrics, color="purple")
plt.close()
last_time = plot_stats(title, last_time)


# @profile
# run with kernprof -l generacion_imagenes.py; python3 -m line_profiler generacion_imagenes.py.lprof
def calculate_p_values_diferencias(df_vmr, df_force, csv_name='distribuciones_diferencias', n=100000):
    filename = os.path.join(path, f"{csv_name}_{n}.csv")
    if os.path.exists(filename):
        df_diferencias = pd.read_csv(filename, index_col=0)
        return df_diferencias

    df_vmr['perturbacion'] = 'vmr'
    df_force['perturbacion'] = 'force'
    df_series_merged = pd.concat([df_vmr.copy(),df_force.copy()])
    df_series_merged['serie'] = df_series_merged.sujeto + '-' + df_series_merged.perturbacion
    lista_series = list(df_series_merged['serie'].unique()) 
    len_vmr = len(df_vmr.sujeto.unique())
    

    diferencias_dict = {}

    median_vmr_original = df_vmr.sort_values('x_axis').groupby(['x_axis'])
    median_force_original = df_force.sort_values('x_axis').groupby(['x_axis'])
    for metric in metrics:
        metric_median_vmr_original = median_vmr_original[metric].median()
        metric_median_force_original = median_force_original[metric].median()
        diferencias_originales_list = list(metric_median_vmr_original - metric_median_force_original)  

        diferencias_dict[metric] = {}  
        diferencias_dict[metric]['val'] = diferencias_originales_list
        len_trials = len(diferencias_originales_list)
        diferencias_dict[metric]['colas'] = [0] * len_trials
        diferencias_dict[metric]['total'] = [0] * len_trials
        diferencias_dict[metric]['p_val'] = [0] * len_trials

    for i in range(n):
        if i%1000 == 0: print(f'{i}/{n}')
        random.shuffle(lista_series)
        vmr_ficticio = lista_series[0:len_vmr]
        force_ficticio = lista_series[len_vmr:]
        df_vmr_ficticio = df_series_merged[df_series_merged.serie.isin(vmr_ficticio)].sort_values('x_axis').groupby(['x_axis'])
        df_force_ficticio = df_series_merged[df_series_merged.serie.isin(force_ficticio)].sort_values('x_axis').groupby(['x_axis'])
        for metric in metrics:
            metric_diferencia = list(df_vmr_ficticio[metric].median() - df_force_ficticio[metric].median())
            for i in range(len(metric_diferencia)):
                shuffle_val = metric_diferencia[i]
                original_val = diferencias_dict[metric]['val'][i]

                if np.abs(original_val) < shuffle_val:
                    diferencias_dict[metric]['colas'][i] += 1

                if -np.abs(original_val) > shuffle_val:
                    diferencias_dict[metric]['colas'][i] += 1
                
                diferencias_dict[metric]['total'][i] += 1
    
    df_diferencias = pd.DataFrame()
    for metric in metrics:
        colas = diferencias_dict[metric]['colas']
        total = diferencias_dict[metric]['total']
        val = diferencias_dict[metric]['val']
        for i in range(len_trials):
            diferencias_dict[metric]['p_val'][i] = colas[i] / total[i] 
        df_diferencias[f'{metric}_val'] = val
        p_val = diferencias_dict[metric]['p_val']
        p_val_corrected = fdrcorrection(p_val, method='poscorr')
        df_diferencias[f'{metric}_p_val'] = p_val
        df_diferencias[f'{metric}_p_val_corrected_bool'] = p_val_corrected[0]
        df_diferencias[f'{metric}_p_val_corrected_val'] = p_val_corrected[1]        

    df_diferencias.to_csv(filename,index=True)
    return df_diferencias



title = "8. Analisis de diferencias entre las perturbaciones"
def plot_diferencias_significativas_mediana(df_vmr, df_force, title, metrics, show_text=True, text_offset=0, blockName_key="bloque_efectivo"):
    fig, axs = create_axs(row_size=len(metrics), sharex='all', figsize=[6.4, 6.4*1.5])
    fig.suptitle(title)
    blockNames = list(df_vmr[blockName_key].unique())

    df_diferencias = calculate_p_values_diferencias(df_vmr, df_force, csv_name='distribuciones_diferencias')

    for blockName in blockNames:
        block_vmr = df_vmr[df_vmr[blockName_key]==blockName].groupby("x_axis").median()
        block_force = df_force[df_force[blockName_key]==blockName].groupby("x_axis").median()
        block_median_diferencias = block_vmr - block_force
        subplot_i = 0
        for metric in metrics:
            ax = axs[subplot_i]
            median_series = block_median_diferencias[metric]
            line, = ax.plot(block_median_diferencias.index, median_series)
            
            # Nombres de los bloques en el grafico
            if show_text:
                x_text = np.mean(median_series.index)
                max_y = df_diferencias[f'{metric}_val'].max()
                min_y = df_diferencias[f'{metric}_val'].min()
                y_text = max_y + (max_y - min_y) * text_offset
                text_color = line.get_color()
                ax.text(x_text, y_text, blockName, horizontalalignment='center', verticalalignment='top', fontsize=10, color=text_color)
            ax.set_xlabel('numero de trial', fontsize=10)
            ax.set_ylabel(metric.replace("_", " "), fontsize=10)
            subplot_i += 1


    subplot_i = 0
    for metric in metrics:
        ax = axs[subplot_i]
        ax.axhline(y=0, color='k', ls='dashed')
        diferencias_significativas_metric = df_diferencias[df_diferencias[f'{metric}_p_val_corrected_bool']==True][f'{metric}_val']
        ax.scatter(diferencias_significativas_metric.index, diferencias_significativas_metric, color='green')
        subplot_i += 1

    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)

plot_diferencias_significativas_mediana(df_vmr, df_force, title, metrics)
plt.close()
last_time = plot_stats(title, last_time)

title = '9. Rapidez'
def plot_rapidez(df_perturbacion, bloque_efectivo, plot_trials, title='Plot rapidez', bucket_size_ms = 5):
    fig, axs = create_axs(row_size=len(plot_trials), sharey='all', sharex='all')
    fig.suptitle(title)
    #
    for sujeto in df_perturbacion.sujeto.unique():
        df_sujeto = df_perturbacion[(df_perturbacion.sujeto == sujeto)].copy()
        df_sujeto = df_sujeto[df_sujeto.bloque_efectivo == bloque_efectivo]
        df_sujeto = df_sujeto[df_sujeto.blockTrialSuccessN.isin(plot_trials)]
        #
        df_sujeto_full = read_file_for_sujeto(sujeto, columns)
        df_sujeto_full = df_sujeto_full[df_sujeto_full.trial.isin(df_sujeto.trial.unique())]
        #
        for i in range(len(plot_trials)):
            blockTrialSuccessN = plot_trials[i]
            df_trial = df_sujeto[df_sujeto.blockTrialSuccessN == blockTrialSuccessN]
            trial, = df_trial.trial.unique()
            #
            # Keep only time between beeps
            first_beep, = df_trial.first_beep.unique()
            second_beep, = df_trial.second_beep.unique()
            df_trial_full = df_sujeto_full[df_sujeto_full.trial == trial].copy()
            df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] < first_beep].index, inplace = True)
            df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] > second_beep].index, inplace = True)
            #
            df_trial_full["timeMsAbs"] = df_trial_full.timeMs - df_trial_full.timeMs.min()
            df_trial_full["timeMsAbsBucket"] = (df_trial_full.timeMsAbs // bucket_size_ms).astype(int)
            grouped_ms = df_trial_full.groupby("timeMsAbsBucket")
            time = []
            v = []
            for (timeMsAbsBucket), group_ms in grouped_ms:
                d = distance(group_ms)
                dt = (group_ms.timeMsAbs.max() - group_ms.timeMsAbs.min())/1000
                if dt != 0:
                    time += [timeMsAbsBucket * bucket_size_ms]
                    v += [d/dt]
            #
            ax = axs[i]
            ax.plot(time, v)
            ax.set_ylabel('Rapidez [cm/s]')
            ax.set_xlabel('Tiempo [ms]')
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500) 

# plot_rapidez(df_vmr, 'perturbacion', plot_trials=[1, 2, 20], title=title+' perturbacion VMR')
# plot_rapidez(df_vmr, 'aftereffects', plot_trials=[1, 2, 20], title=title+' aftereffects VMR')
# plot_rapidez(df_force, 'perturbacion', plot_trials=[1, 2, 20], title=title+' perturbacion fuerza')
# plot_rapidez(df_force, 'aftereffects', plot_trials=[1, 2, 20], title=title+' aftereffects fuerza')
# plt.close()
# last_time = plot_stats(title, last_time)
# plt.close()
# last_time = plot_stats(title, last_time)
# plt.close()
# last_time = plot_stats(title, last_time)
# plt.close()
# last_time = plot_stats(title, last_time)

def plot_error_espacial_temporal(df_perturbacion, bloque_efectivo, ax, metrics, color, label=None, title='Error espacial y temporal'):
    # ax.axis('equal')
    # ax.set_box_aspect(1)
    df_bloque = df_perturbacion[df_perturbacion.bloque_efectivo == bloque_efectivo].copy()
    median_df = df_bloque.groupby("x_axis").median()
    ax.plot(median_df[metrics[0][0]], median_df[metrics[1][0]], label=label, color=color)
    ax.scatter(median_df[metrics[0][0]], median_df[metrics[1][0]], s=1, color=color)
    ax.set_xlabel(metrics[0][1])
    ax.set_ylabel(metrics[1][1])
    plt.legend(loc="upper right")
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500)


title = '10. Error de area absoluto y temporal'
fig, axs = create_axs(col_size=1)
fig.suptitle(title)
metrics = [('area_error_abs', 'Error de area absoluto'), ('temporal_error', 'Error temporal')]
plot_error_espacial_temporal(df_vmr, 'perturbacion', axs, metrics, color='limegreen', label="perturbacion VMR", title=title)
plot_error_espacial_temporal(df_vmr, 'aftereffects', axs, metrics, color='darkgreen', label="aftereffects VMR", title=title)
plot_error_espacial_temporal(df_force, 'perturbacion', axs, metrics, color='orchid', label="perturbacion fuerza", title=title)
plot_error_espacial_temporal(df_force, 'aftereffects', axs, metrics, color='purple', label="aftereffects fuerza", title=title)
plt.close()
last_time = plot_stats(title, last_time)

title = '10. Error de area signado y temporal'
fig, axs = create_axs()
fig.suptitle(title)
metrics = [('area_error', 'Error de area signado'), ('temporal_error', 'Error temporal')]
plot_error_espacial_temporal(df_vmr, 'perturbacion', axs, metrics, color='limegreen', label="perturbacion VMR", title=title)
plot_error_espacial_temporal(df_vmr, 'aftereffects', axs, metrics, color='darkgreen', label="aftereffects VMR", title=title)
plot_error_espacial_temporal(df_force, 'perturbacion', axs, metrics, color='orchid', label="perturbacion fuerza", title=title)
plot_error_espacial_temporal(df_force, 'aftereffects', axs, metrics, color='purple', label="aftereffects fuerza", title=title)
plt.close()
last_time = plot_stats(title, last_time)

title = '11. Posicion y velocidad para un sujeto'
sujetos_vmr = list(df_vmr.sujeto.unique())
sujetos_force = list(df_force.sujeto.unique())
sujetos_ambos = [i for i in sujetos_vmr if i in sujetos_force]
sujeto = sujetos_ambos[0]
fig, axs = create_axs()

def posicion_y_velocidad_trials(df_perturbacion, sujeto, bloque_efectivo, plot_trials, label, colors, ax, bucket_size_ms=5, title='Posicion y velocidad para un sujeto'):
    df_sujeto = df_perturbacion[(df_perturbacion.sujeto == sujeto)].copy()
    df_sujeto = df_sujeto[df_sujeto.bloque_efectivo == bloque_efectivo]
    df_sujeto = df_sujeto[df_sujeto.blockTrialSuccessN.isin(plot_trials)]
    df_sujeto_full = read_file_for_sujeto(sujeto, columns)
    df_sujeto_full = df_sujeto_full[df_sujeto_full.trial.isin(df_sujeto.trial.unique())]
    for i in range(len(plot_trials)):
        blockTrialSuccessN = plot_trials[i]
        df_trial = df_sujeto[df_sujeto.blockTrialSuccessN == blockTrialSuccessN]
        trial, = df_trial.trial.unique()
        #
        # Keep only time between beeps
        first_beep, = df_trial.first_beep.unique()
        second_beep, = df_trial.second_beep.unique()
        df_trial_full = df_sujeto_full[df_sujeto_full.trial == trial].copy()
        df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] < first_beep].index, inplace = True)
        df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] > second_beep].index, inplace = True)
        #
        df_trial_full["timeMsAbs"] = df_trial_full.timeMs - df_trial_full.timeMs.min()
        df_trial_full["timeMsAbsBucket"] = (df_trial_full.timeMsAbs // bucket_size_ms).astype(int)
        # Rotate
        angle, = df_trial_full.angle.unique()
        df_trial_full = rotate_trial_data(df_trial_full, angle)
        grouped_ms = df_trial_full.groupby("timeMsAbsBucket")
        distance_transversal = []
        v = []
        for (timeMsAbsBucket), group_ms in grouped_ms:
            d = distance(group_ms)
            dt = (group_ms.timeMsAbs.max() - group_ms.timeMsAbs.min())/1000
            if dt != 0:
                v += [d/dt]
                distance_transversal += [group_ms.y.mean()]
        #
        ax.plot(distance_transversal, v, color=colors[i], label=f"{label} trial {blockTrialSuccessN}")
        ax.set_ylabel('Rapidez [cm/s]')
        ax.set_xlabel('Distancia transversal [cm]')
    plt.legend(loc="upper right")
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500) 

colors = ['orchid', 'darkorchid', 'purple']
posicion_y_velocidad_trials(df_vmr, sujeto, 'perturbacion', ax=axs, plot_trials=[1, 2, 20], label='VMR', colors=colors, title=title)

colors = ['lime', 'limegreen', 'darkgreen']
posicion_y_velocidad_trials(df_force, sujeto, 'perturbacion', ax=axs, plot_trials=[1, 2, 20], label='fuerza', colors=colors, title=title)
plt.close()
last_time = plot_stats(title, last_time)

def plots_velocidad_posicion_transversal(df_perturbacion, bloque_efectivo, plot_trials, label, title='Plot velocidad transversal', bucket_size_ms = 5, mode='velocidad', figsize=None):
    fig, axs = create_axs(row_size=len(plot_trials), sharey='all', sharex='all', figsize=figsize)
    fig.suptitle(title)
    #
    for sujeto in df_perturbacion.sujeto.unique():
        df_sujeto = df_perturbacion[(df_perturbacion.sujeto == sujeto)].copy()
        df_sujeto = df_sujeto[df_sujeto.bloque_efectivo == bloque_efectivo]
        df_sujeto = df_sujeto[df_sujeto.blockTrialSuccessN.isin(plot_trials)]
        #
        df_sujeto_full = read_file_for_sujeto(sujeto, columns)
        df_sujeto_full = df_sujeto_full[df_sujeto_full.trial.isin(df_sujeto.trial.unique())]
        #
        for i in range(len(plot_trials)):
            blockTrialSuccessN = plot_trials[i]
            df_trial = df_sujeto[df_sujeto.blockTrialSuccessN == blockTrialSuccessN]
            trial, = df_trial.trial.unique()
            #
            # Keep only time between beeps
            first_beep, = df_trial.first_beep.unique()
            second_beep, = df_trial.second_beep.unique()
            df_trial_full = df_sujeto_full[df_sujeto_full.trial == trial].copy()
            df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] < first_beep].index, inplace = True)
            df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] > second_beep].index, inplace = True)
            #
            df_trial_full["timeMsAbs"] = df_trial_full.timeMs - df_trial_full.timeMs.min()
            df_trial_full["timeMsAbsBucket"] = (df_trial_full.timeMsAbs // bucket_size_ms).astype(int)
            # Rotate
            angle, = df_trial_full.angle.unique()
            df_trial_full = rotate_trial_data(df_trial_full, angle)
            grouped_ms = df_trial_full.groupby("timeMsAbsBucket")
            time = []
            vy = []
            distance_transversal = []
            for (timeMsAbsBucket), group_ms in grouped_ms:
                dy, = total_distance_vect(group_ms).y.values
                dt = (group_ms.timeMsAbs.max() - group_ms.timeMsAbs.min())/1000
                if dt != 0 and dt > 4/1000:
                    time += [timeMsAbsBucket * bucket_size_ms]
                    vy += [dy/dt]
                    distance_transversal += [group_ms.y.mean()]
            #
            ax = axs[i]
            if mode == 'velocidad':
                ax.plot(time, vy)
                ax.set_ylabel('Velocidad transversal [cm/s]', fontsize=10)
            elif mode == 'posicion':
                ax.plot(time, distance_transversal)
                ax.set_ylabel('Distancia transversal [cm]', fontsize=10)
            ax.set_xlabel('Tiempo [ms]', fontsize=10)
            ax.set_title(f"{bloque_efectivo} {label} trial {blockTrialSuccessN}")
            ax.axhline(y=0, color='k', ls='dashed')
    plt.savefig(os.path.join(path, f"{title.replace(' ', '_')}.png") , dpi = 500) 


# title = "12. Velocidad transversal"

# plots_velocidad_posicion_transversal(df_vmr, 'perturbacion', plot_trials=[1, 5, 10, 15, 20], title=title+' perturbacion VMR', label='VMR', mode='velocidad', figsize=[6.4, 6.4*1.5])
# plots_velocidad_posicion_transversal(df_vmr, 'aftereffects', plot_trials=[1, 5, 10, 15, 20], title=title+' aftereffects VMR', label='VMR', mode='velocidad', figsize=[6.4, 6.4*1.5])
# plots_velocidad_posicion_transversal(df_force, 'perturbacion', plot_trials=[1, 5, 10, 15, 20], title=title+' perturbacion fuerza', label='fuerza', mode='velocidad', figsize=[6.4, 6.4*1.5])
# plots_velocidad_posicion_transversal(df_force, 'aftereffects', plot_trials=[1, 5, 10, 15, 20], title=title+' aftereffects fuerza', label='fuerza', mode='velocidad', figsize=[6.4, 6.4*1.5])
# plt.close()
# plt.close()
# plt.close()
# plt.close()
# last_time = plot_stats(title, last_time)


# title = '13. Posicion transversal'

# plots_velocidad_posicion_transversal(df_vmr, 'perturbacion', plot_trials=[1, 5, 10, 15, 20], title=title+' perturbacion VMR', label='VMR', mode='posicion', figsize=[6.4, 6.4*1.5])
# plots_velocidad_posicion_transversal(df_vmr, 'aftereffects', plot_trials=[1, 5, 10, 15, 20], title=title+' aftereffects VMR', label='VMR', mode='posicion', figsize=[6.4, 6.4*1.5])
# plots_velocidad_posicion_transversal(df_force, 'perturbacion', plot_trials=[1, 5, 10, 15, 20], title=title+' perturbacion fuerza', label='fuerza', mode='posicion', figsize=[6.4, 6.4*1.5])
# plots_velocidad_posicion_transversal(df_force, 'aftereffects', plot_trials=[1, 5, 10, 15, 20], title=title+' aftereffects fuerza', label='fuerza', mode='posicion', figsize=[6.4, 6.4*1.5])
# plt.close()
# plt.close()
# plt.close()
# plt.close()
# last_time = plot_stats(title, last_time)



def posicion_y_velocidad_transversal(df_perturbacion, sujeto, bloque_efectivo, plot_trials, label, bucket_size_ms=10, normalize=False, baseline="start", title='Posicion y velocidad para un sujeto'):
    fig, ax = create_axs()
    df_sujeto = df_perturbacion[(df_perturbacion.sujeto == sujeto)].copy()
    df_sujeto = df_sujeto[df_sujeto.bloque_efectivo == bloque_efectivo]
    df_sujeto = df_sujeto[df_sujeto.blockTrialSuccessN.isin(plot_trials)]
    df_sujeto_full = read_file_for_sujeto(sujeto, columns)
    df_sujeto_full = df_sujeto_full[df_sujeto_full.trial.isin(df_sujeto.trial.unique())]
    # colormap = plt.cm.winter
    # colors = [colormap(i) for i in np.linspace(0, 1, len(plot_trials))]
    ax.axhline(0, color='k', ls='dashed', linewidth=1)
    ax.axvline(0, color='k', ls='dashed', linewidth=1)    
    for i in range(len(plot_trials)):
        blockTrialSuccessN = plot_trials[i]
        df_trial = df_sujeto[df_sujeto.blockTrialSuccessN == blockTrialSuccessN]
        trial, = df_trial.trial.unique()
        #
        # Keep only time between beeps
        first_beep, = df_trial.first_beep.unique()
        second_beep, = df_trial.second_beep.unique()
        df_trial_full = df_sujeto_full[df_sujeto_full.trial == trial].copy()
        df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] < first_beep].index, inplace = True)
        df_trial_full.drop(df_trial_full[df_trial_full['timeMs'] > second_beep].index, inplace = True)
        #
        df_trial_full["timeMsAbs"] = df_trial_full.timeMs - df_trial_full.timeMs.min()
        df_trial_full["timeMsAbsBucket"] = (df_trial_full.timeMsAbs // bucket_size_ms).astype(int)
        # Rotate
        angle, = df_trial_full.angle.unique()
        df_trial_full = rotate_trial_data(df_trial_full, angle)
        grouped_ms = df_trial_full.groupby("timeMsAbsBucket")
        distance_transversal = []
        vy = []
        for (timeMsAbsBucket), group_ms in grouped_ms:
            dy, = total_distance_vect(group_ms).y.values
            dt = (group_ms.timeMsAbs.max() - group_ms.timeMsAbs.min())/1000
            if dt != 0 and dt > 4/1000:
                vy += [dy/dt]
                distance_transversal += [group_ms.y.mean()]
        
        if baseline == "start":
            # Restar primer valor
            vy_first_value = vy[0]
            distance_transversal_first_value = distance_transversal[0]
            vy = [i-vy_first_value for i in vy]
            distance_transversal = [i-distance_transversal_first_value for i in distance_transversal]        
        elif baseline == "end":
            # Restar ultimo valor
            vy_last_value = vy[-1]
            distance_transversal_last_value = distance_transversal[-1]
            vy = [i-vy_last_value for i in vy]
            distance_transversal = [i-distance_transversal_last_value for i in distance_transversal]

        if normalize:
            # Normalizar a 1 el valor max
            vy_max_val = np.abs(max(vy, key=abs))
            distance_transversal_max_val = np.abs(max(distance_transversal, key=abs))
            vy = [i/vy_max_val for i in vy]
            distance_transversal = [i/distance_transversal_max_val for i in distance_transversal]   

        # Plot fases
        line, = ax.plot(distance_transversal, vy, label=f"{bloque_efectivo} {label} trial {blockTrialSuccessN}")
        # Plot valor inicial
        ax.scatter(distance_transversal[0], vy[0], color=line.get_color())
    ax.set_ylabel('Velocidad transversal [cm/s]', fontsize=10)
    ax.set_xlabel('Distancia transversal [cm]', fontsize=10)

    plt.legend(loc="upper right")
    plt.savefig(os.path.join(path, "imagen_14", f"{title.replace(' ', '_')}_baseline_{baseline}_normalize_{normalize}.png") , dpi = 500) 

# i = 0
# for sujeto in df_force.sujeto.unique():
#     title = f'14.a.sujeto_{i} Espacio de fases transversal perturbacion fuerza'
#     posicion_y_velocidad_transversal(df_force, sujeto, 'perturbacion', plot_trials=[1, 5, 10, 15, 20], label='fuerza', title=title)
#     plt.close()
#     i += 1
# last_time = plot_stats(title, last_time)

# i = 0
# for sujeto in df_vmr.sujeto.unique():
#     title = f'14.b.sujeto_{i} Espacio de fases transversal perturbacion VMR'
#     posicion_y_velocidad_transversal(df_vmr, sujeto, 'perturbacion', plot_trials=[1, 5, 10, 15, 20], label='VMR', title=title)
#     plt.close()
#     i += 1
# last_time = plot_stats(title, last_time)

# i = 0
# for sujeto in df_force.sujeto.unique():
#     title = f'14.c.sujeto_{i} Espacio de fases transversal aftereffects fuerza'
#     posicion_y_velocidad_transversal(df_force, sujeto, 'aftereffects', plot_trials=[1, 5, 10, 15, 20], label='fuerza', title=title)
#     plt.close()
#     i += 1
# last_time = plot_stats(title, last_time)

# i = 0
# for sujeto in df_vmr.sujeto.unique():
#     title = f'14.d.sujeto_{i} Espacio de fases transversal aftereffects VMR'
#     posicion_y_velocidad_transversal(df_vmr, sujeto, 'aftereffects', plot_trials=[1, 5, 10, 15, 20], label='VMR', title=title)
#     plt.close()
#     i += 1
# last_time = plot_stats(title, last_time)

def get_angle(x,y):
    if x == 0:
        if y > 0:
            division = np.inf
        elif y < 0:
            division = -np.inf
        elif y==0:
            division = np.NaN
    else:
        division = y / x
    angle = np.arctan(division)
    return angle

def resample_by_interpolation(signal, n):
    resampled_signal = np.interp(
        np.linspace(0.0, 1.0, n, endpoint=False),  # where to interpret
        np.linspace(0.0, 1.0, len(signal), endpoint=False),  # known positions
        signal,  # known data points
    )
    return resampled_signal

def posicion_y_velocidad_transversal_promedios(df_perturbacion, bloque_efectivo, plot_trials, bucket_size_ms=10, normalize=False, resample=True, baseline="start", title='Posicion y velocidad promedio'):
    figsize=[6.4, 6.4*2]
    len_metrics = 3
    fig1 = plt.figure(figsize=figsize, constrained_layout=True)
    gs = GridSpec(len(plot_trials)*len_metrics, 2, figure=fig1)

    # Figura promedios 
    fig2, ax2 = create_axs()
    ax2.axhline(0, color='k', ls='dashed', linewidth=1)
    ax2.axvline(0, color='k', ls='dashed', linewidth=1)
    ax2.set_xlabel('Dist. transv. norm.', fontsize=10)
    ax2.set_ylabel('Vel. transv. norm.', fontsize=10)
    # ax2.set_xlim([-1, 1])
    # ax2.set_ylim([-1, 1])
    
    
    trials_dataset = pd.DataFrame()

    for i in range(len(plot_trials)):
        # Subplot fases
        trial_ax = fig1.add_subplot(gs[len_metrics*i:len_metrics*i+len_metrics, 0])
        # if i is not range(len(plot_trials))[-1]:
        #     trial_ax.get_xaxis().set_visible(False)

        trial_ax.axhline(0, color='k', ls='dashed', linewidth=1)
        trial_ax.axvline(0, color='k', ls='dashed', linewidth=1)
        trial_ax.set_xlabel('Dist. transv. norm.', fontsize=10)
        trial_ax.set_ylabel('Vel. transv. norm.', fontsize=10)

        # trial_ax.set_xlim([-1, 1])
        # trial_ax.set_ylim([-1, 1])

        # Subplot vy y dist transv
        linea_dt_ax = fig1.add_subplot(gs[len_metrics*i, 1])
        linea_vy_ax = fig1.add_subplot(gs[len_metrics*i+1, 1])
        linea_angle_ax = fig1.add_subplot(gs[len_metrics*i+2, 1])
        
        linea_dt_ax.get_xaxis().set_visible(False)
        linea_vy_ax.get_xaxis().set_visible(False)
        linea_angle_ax.get_xaxis().set_visible(False)

        linea_dt_ax.axhline(0, color='k', ls='dashed', linewidth=1)   
        linea_vy_ax.axhline(0, color='k', ls='dashed', linewidth=1)
        linea_angle_ax.axhline(0, color='k', ls='dashed', linewidth=1)   
        
        linea_dt_ax.set_ylabel('Dist. transv. norm.', fontsize=10)
        linea_vy_ax.set_ylabel('Vel. transv. norm.', fontsize=10)
        linea_angle_ax.set_ylabel('Angulo', fontsize=10)

        # Analisis
        blockTrialSuccessN = plot_trials[i]
        df_trial = df_perturbacion[df_perturbacion.bloque_efectivo == bloque_efectivo].copy()
        df_trial = df_trial[df_trial.blockTrialSuccessN == blockTrialSuccessN]
        
        grouped_sujeto = df_trial.groupby("sujeto")
        for sujeto, df_sujeto  in grouped_sujeto:
            trial, = df_sujeto.trial.unique()   
            df_sujeto_full = read_file_for_sujeto(sujeto, columns)
            df_sujeto_full = df_sujeto_full[df_sujeto_full.trial==trial]

            # Keep only time between beeps
            first_beep, = df_sujeto.first_beep.unique()
            second_beep, = df_sujeto.second_beep.unique()
            df_sujeto_full = df_sujeto_full[df_sujeto_full.trial == trial].copy()
            df_sujeto_full.drop(df_sujeto_full[df_sujeto_full['timeMs'] < first_beep].index, inplace = True)
            df_sujeto_full.drop(df_sujeto_full[df_sujeto_full['timeMs'] > second_beep].index, inplace = True)

            # Time buckets
            df_sujeto_full["timeMsAbs"] = df_sujeto_full.timeMs - df_sujeto_full.timeMs.min()
            df_sujeto_full["timeMsAbsBucket"] = (df_sujeto_full.timeMsAbs // bucket_size_ms).astype(int)
            
            # Rotate
            angle, = df_sujeto_full.angle.unique()
            df_sujeto_full = rotate_trial_data(df_sujeto_full, angle)

            # Group by ms bucket
            grouped_ms = df_sujeto_full.groupby("timeMsAbsBucket")
            distance_transversal = []
            vy = []

            for (timeMsAbsBucket), group_ms in grouped_ms:
                dy, = total_distance_vect(group_ms).y.values
                dt = (group_ms.timeMsAbs.max() - group_ms.timeMsAbs.min())/1000
                if dt != 0 and dt > 4/1000:
                    vy += [dy/dt]
                    distance_transversal += [group_ms.y.mean()]
            
            if baseline == "start":
                # Restar primer valor
                vy_first_value = vy[0]
                distance_transversal_first_value = distance_transversal[0]
                vy = [i-vy_first_value for i in vy]
                distance_transversal = [i-distance_transversal_first_value for i in distance_transversal]        
            elif baseline == "end":
                # Restar ultimo valor
                vy_last_value = vy[-1]
                distance_transversal_last_value = distance_transversal[-1]
                vy = [i-vy_last_value for i in vy]
                distance_transversal = [i-distance_transversal_last_value for i in distance_transversal]

            if normalize:
                # Normalizar a 1 el valor max
                vy_max_val = np.abs(max(vy, key=abs))
                distance_transversal_max_val = np.abs(max(distance_transversal, key=abs))
                vy = [i/vy_max_val for i in vy]
                distance_transversal = [i/distance_transversal_max_val for i in distance_transversal]   


            if resample:
                # Signal resample 
                N_points = 100
                resampled_vy = resample_by_interpolation(vy, N_points)
                resampled_distance_transversal = resample_by_interpolation(distance_transversal, N_points)
                points = [i+1 for i in range(N_points)]
            
            else:
                resampled_vy = vy
                resampled_distance_transversal = distance_transversal
                points = [i*bucket_size_ms for i in range(len(vy))]

            sujeto_dataset = pd.DataFrame({
                    'sujeto': sujeto,
                    'bloque_efectivo': bloque_efectivo,
                    'trial': blockTrialSuccessN,
                    'resampled_vy': resampled_vy, 
                    'resampled_distance_transversal': resampled_distance_transversal, 
                    'point': points
                    })
            sujeto_dataset['angle'] = sujeto_dataset.apply(lambda x: get_angle(x['resampled_distance_transversal'],x['resampled_vy']), axis=1)
            trials_dataset = trials_dataset.append(sujeto_dataset, ignore_index=True)
            
            # Plot fases
            line, = trial_ax.plot(distance_transversal, vy, alpha=0.25)
            # Plot valor inicial
            trial_ax.scatter(distance_transversal[0], vy[0], color=line.get_color(), alpha=0.25)
            # Plot vy, dt resampled
            linea_vy_ax.plot(sujeto_dataset.point, sujeto_dataset.resampled_vy, color='grey', alpha=0.25)
            linea_dt_ax.plot(sujeto_dataset.point, sujeto_dataset.resampled_distance_transversal, color='grey', alpha=0.25)
            linea_angle_ax.plot(sujeto_dataset.point, sujeto_dataset.angle, color='grey', alpha=0.25)
        

        # Mediana del trial
        mean_trial = trials_dataset[trials_dataset.trial == blockTrialSuccessN].groupby('point').mean()
        sem_trial = trials_dataset[trials_dataset.trial == blockTrialSuccessN].groupby('point').sem()
        
        trial_ax.plot(mean_trial.resampled_distance_transversal, mean_trial.resampled_vy, color='blue', label=f'Promedio trial {blockTrialSuccessN}')
        trial_ax.legend(loc="upper right")
        ax2.plot(mean_trial.resampled_distance_transversal, mean_trial.resampled_vy, label=f'Promedio trial {blockTrialSuccessN}')
        ax2.legend(loc="upper right")
        
        linea_vy_ax.plot(mean_trial.index, mean_trial.resampled_vy, color='blue')
        linea_vy_ax.fill_between(
            x=mean_trial.index, 
            y1=mean_trial.resampled_vy - sem_trial.resampled_vy,
            y2=mean_trial.resampled_vy + sem_trial.resampled_vy,
            alpha=0.25,
            color='blue'
            )
        linea_dt_ax.plot(mean_trial.index, mean_trial.resampled_distance_transversal, color='blue')
        linea_dt_ax.fill_between(
            x=mean_trial.index, 
            y1=mean_trial.resampled_distance_transversal - sem_trial.resampled_distance_transversal,
            y2=mean_trial.resampled_distance_transversal + sem_trial.resampled_distance_transversal,
            alpha=0.25,
            color='blue'
            )
        linea_angle_ax.plot(mean_trial.index, mean_trial.angle, color='blue')
        linea_angle_ax.fill_between(
            x=mean_trial.index, 
            y1=mean_trial.angle - sem_trial.angle,
            y2=mean_trial.angle + sem_trial.angle,
            alpha=0.25,
            color='blue'
            )

    plt.figure(fig1.number)
    plt.savefig(os.path.join(path, "imagen_15", f"{title.replace(' ', '_')}_{bucket_size_ms}ms_normalize_{normalize}_resample_{resample}.png") , dpi = 500) 
    plt.figure(fig2.number)
    plt.savefig(os.path.join(path, "imagen_15", f"{title.replace(' ', '_')}_summary_{bucket_size_ms}ms_normalize_{normalize}_resample_{resample}.png") , dpi = 500) 

plot_trials=[1, 5, 10, 15, 20]
for normalize in [True, False]:
    for resample in [True, False]:
        for bloque in ['perturbacion', 'aftereffects']:
            title = f'15.a Posicion y velocidad promedio {bloque} VMR'
            posicion_y_velocidad_transversal_promedios(df_vmr, bloque, plot_trials=plot_trials, title=title, normalize=normalize, resample=resample)
            plt.close()
            last_time = plot_stats(title, last_time)

            title = '15.b Posicion y velocidad promedio perturbacion Force'
            posicion_y_velocidad_transversal_promedios(df_force, bloque, plot_trials=plot_trials, title=title, normalize=normalize, resample=resample)
            plt.close()
            last_time = plot_stats(title, last_time)          


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Finalizado en {elapsed_time // 60} minutos y {elapsed_time % 60} segundos")


'''
colorblind frineldy colormap 
restar el ultimo punto del trial a cada trial

* normalizado a mismo final/inicio
* normalizacion de escala a valor max en modulo para cada eje 

en todos los casos normalizar a 1 y restar el inicio del trial 
grafico de trials 1,5,10... 20, por cada trial mostrar todos los candidatos y el promedio, y al lado el vy y y con bandas 
para el promedio tomo el resultado de binear cada 10ms, lo paso por scipy signal resample y con esos 100 puntos lo grafico across trials porque todo tienen 100 puntos 
una imagne mas con los datos de los 5 promedios

'''


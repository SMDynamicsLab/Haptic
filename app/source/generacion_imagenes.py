import os 
import pandas as pd
import matplotlib.pyplot as plt
from analisis_datos import * 
import numpy as np
from matplotlib.pyplot import cm

file= os.path.join(path, "Merge_analisis.csv")
df = pd.read_csv(file, index_col=False)
df = df[df.trialSuccess == 1]

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

def create_axs(row_size=1, col_size=1, sharex=False, sharey=False, figsize=None):
    fig, axs = plt.subplots(row_size, col_size, sharex=sharex, sharey=sharey, constrained_layout=True, figsize=figsize)
    for ax in axs.flat:
            plt.setp(ax.get_xticklabels(), fontsize=10)
            plt.setp(ax.get_yticklabels(), fontsize=10)
    return fig, axs


def read_file_for_sujeto(sujeto, columns):
    file = files_dict[sujeto]["file"]
    file_path = os.path.join(path, files_dict[sujeto]["path"])
    file = os.path.join(file_path, file)
    df_sujeto = pd.read_csv(file, names=columns, index_col=False)
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
            # Fix coordinates (x to -x & *100)
            group['x'] = -group['x']*100  # [cm]
            group['y'] = group['y']*100   # [cm]
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

from scipy import stats
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

from matplotlib.cbook import boxplot_stats
import seaborn as sns
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

import matplotlib.patches as mpatches
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


title = "1b.Errores sujeto con vmr al comienzo"
plot_errores_sujeto(df_sujeto_vmr, title)

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

title = "2b.Errores sujeto con fuerza al comienzo"
plot_errores_sujeto(df_sujeto_force, title)

'''
3a. Pendiente de la primer mitad y mediana de la segunda mitad visualizada en un sujeto con vmr
3b. Boxplot de todos los sujetos, para pendiente de la primer mitad y mediana de la segunda mitad
3c. Igual que 3b pero sin los outliers, numerado por iteracion
TODO: usar RLM https://www.statsmodels.org/dev/examples/notebooks/generated/robust_models_0.html


'''
title = "3a. Pendiente y mediana - criterios de outliers - ejemplo sujeto"
df_sujeto_vmr = df[(df.sujeto == sujeto) & (df.blockName == "VMR")]
plot_pendiente_y_mediana_sujeto(df_sujeto_vmr, title)

title = "3b. Boxplot de pendiente y mediana"
outliers_dict = plot_boxplot_pendiente_y_mediana(df, title)
df_sin_outliers, len_outliers = sacar_outliers(df, outliers_dict)


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

# title = "4c. Errores - promedio y banda standard error mean - sin outliers"
# fig, axs = create_axs(row_size=len(metrics), sharex='all')
# plot_promedio(df_sin_outliers, title, fig, axs, metrics)
# plot_banda_sem(df_sin_outliers, title, fig, axs, metrics)


'''
5. Comparacion de sujetos con condiciones contrabalanceadas - Errores
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
red_patch = mpatches.Patch(color='purple', label=f"Fuerza")
blue_patch = mpatches.Patch(color='green', label=f"VMR")
for ax in axs:
    ax.legend(handles=[red_patch, blue_patch], loc='best', fontsize=5)    

plot_mediana(df_vmr, title, fig, axs, metrics, show_text=True, global_text_color='black', color="purple", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_vmr, title, fig, axs, metrics, color="purple")
plot_mediana(df_force, title, fig, axs, metrics, show_text=False, color="green", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_force, title, fig, axs, metrics, color="green")


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
red_patch = mpatches.Patch(color='purple', label=f"Fuerza")
blue_patch = mpatches.Patch(color='green', label=f"VMR")
for ax in axs:
    ax.legend(handles=[red_patch, blue_patch], loc='best', fontsize=5)    

plot_mediana(df_vmr, title, fig, axs, metrics, show_text=True, global_text_color='black', color="purple", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_vmr, title, fig, axs, metrics, color="purple")
plot_mediana(df_force, title, fig, axs, metrics, show_text=False, color="green", blockName_key='bloque_efectivo')
plot_banda_sem_median(df_force, title, fig, axs, metrics, color="green")



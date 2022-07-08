import os 
import pandas as pd
import matplotlib.pyplot as plt
from analisis_datos import * 
import numpy as np
from matplotlib.pyplot import cm

file= os.path.join(path, "Merge_analisis.csv")
df = pd.read_csv(file, index_col=False)
df = df[df.trialSuccess == 1]

metrics = [
    'area_error',
    'area_error_abs',
    'd',
    'reproduced_period',
    'temporal_error',
]
block_vars = ['blockName']

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

# Todos los sujetos en un grafico
def plot_sujetos(df, metrics, figure_offset, title="", color_choice = None, alpha=1, showLabel=False): 

    sujetosN = len(df.sujeto.unique())
    colors_sujetos = cm.rainbow(np.linspace(0, 1, sujetosN))
    color_i = 0
    grouped_sujeto = df.groupby("sujeto")
    for sujeto, group_sujeto in grouped_sujeto:
        if not color_choice:
            color = colors_sujetos[color_i]
        else:
            color = color_choice
        grouped_block = group_sujeto.groupby(block_vars)
        for (blockName), block_group in grouped_block:
            figure_i = 1
            for metric in metrics:
                plt.figure(figure_offset + figure_i)
                params = {
                    "color": color,
                    "alpha": alpha,
                }
                if showLabel and blockName=="Adaptacion":
                    params['label'] = sujeto

                plt.plot(block_group.x_axis, block_group[metric], **params)
                if showLabel: 
                    plt.legend(loc="upper left", fontsize=5)
                plt.title(metric + f" {title}")
                plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
                figure_i += 1
        color_i+=1

def plot_promedio(df, metrics, figure_offset, title="promedio"):
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        figure_i = 1
        for metric in metrics:
            plt.figure(figure_offset + figure_i)
            avg_series = mean_df[metric]
            plt.plot(mean_df.index, avg_series, label=blockName)
            plt.legend(loc="upper left", fontsize=5)
            plt.title(metric + f" {title}")
            plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
            figure_i += 1     

def plot_bandas_std(df, metrics, figure_offset, title ="bandas_std"):
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        std_df = block_group.groupby("x_axis").std()
        figure_i = 1
        for metric in metrics:
            plt.figure(figure_offset + figure_i)
            avg_series = mean_df[metric]
            std_series = std_df[metric]
            plt.fill_between(x=mean_df.index,
                        y1=avg_series - std_series,
                        y2=avg_series + std_series,
                        alpha=0.25
                        )
            plt.title(metric + f" {title}")
            plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
            figure_i += 1  

def plot_bandas_sem(df, metrics, figure_offset, title ="bandas_sem"):
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        sem_df = block_group.groupby("x_axis").sem()
        figure_i = 1
        for metric in metrics:
            plt.figure(figure_offset + figure_i)
            avg_series = mean_df[metric]
            sem_series = sem_df[metric]
            plt.fill_between(x=mean_df.index,
                        y1=avg_series - sem_series,
                        y2=avg_series + sem_series,
                        alpha=0.25
                        )
            plt.title(metric + f" {title}")
            plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
            figure_i += 1 

def plot_mediana(df, metrics, figure_offset, title="mediana"):
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        figure_i = 1
        for metric in metrics:
            plt.figure(figure_offset + figure_i)
            avg_series = median_df[metric]
            plt.plot(median_df.index, avg_series, label=blockName)
            plt.legend(loc="upper left", fontsize=5)
            plt.title(metric + f" {title}")
            plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
            figure_i += 1     

def plot_bandas_mad(df, metrics, figure_offset, title ="bandas_mad"):
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        mad_df = block_group.groupby("x_axis").mad()
        figure_i = 1
        for metric in metrics:
            plt.figure(figure_offset + figure_i)
            avg_series = median_df[metric]
            mad_series = mad_df[metric]
            plt.fill_between(x=median_df.index,
                        y1=avg_series - mad_series,
                        y2=avg_series + mad_series,
                        alpha=0.25
                        )
            plt.title(metric + f" {title}")
            plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
            figure_i += 1  

# Todos los sujetos en un grafico
def axs_plot_sujetos(fig, axs, df, metrics, title="", color_choice = None, alpha=1): 
    fig.suptitle(title)
    sujetosN = len(df.sujeto.unique())
    colors_sujetos = cm.rainbow(np.linspace(0, 1, sujetosN))
    color_i = 0
    grouped_sujeto = df.groupby("sujeto")
    for sujeto, group_sujeto in grouped_sujeto:
        if not color_choice:
            color = colors_sujetos[color_i]
        else:
            color = color_choice
        grouped_block = group_sujeto.groupby(block_vars)
        for (blockName), block_group in grouped_block:
            subplot_i = 0
            for metric in metrics:
                axs[subplot_i].plot(block_group.x_axis, block_group[metric],color=color, alpha=alpha)
                axs[subplot_i].set_title(metric, fontsize=5)
                subplot_i += 1
                
        color_i+=1
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_promedio(fig, axs, df, metrics, title="promedio"):
    fig.suptitle(title)
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        subplot_i = 0
        for metric in metrics:
            avg_series = mean_df[metric]
            axs[subplot_i].plot(mean_df.index, avg_series)
            axs[subplot_i].set_title(metric, fontsize=5)
            subplot_i += 1     
        
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_bandas_std(fig, axs, df, metrics, title ="bandas_std"):
    fig.suptitle(title)
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        std_df = block_group.groupby("x_axis").std()
        subplot_i = 0
        for metric in metrics:
            avg_series = mean_df[metric]
            std_series = std_df[metric]
            axs[subplot_i].fill_between(x=mean_df.index,
                        y1=avg_series - std_series,
                        y2=avg_series + std_series,
                        alpha=0.25
                        )
            axs[subplot_i].set_title(metric, fontsize=5)
            subplot_i += 1  

    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_bandas_sem(fig, axs, df, metrics, title ="bandas_sem"):
    fig.suptitle(title)
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        mean_df = block_group.groupby("x_axis").mean()
        print(mean_df.head(5).index)
        sem_df = block_group.groupby("x_axis").sem()
        subplot_i = 0
        for metric in metrics:
            avg_series = mean_df[metric]
            sem_series = sem_df[metric]
            axs[subplot_i].fill_between(x=mean_df.index,
                        y1=avg_series - sem_series,
                        y2=avg_series + sem_series,
                        alpha=0.25
                        )
            axs[subplot_i].set_title(metric, fontsize=5)
            subplot_i += 1 
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_mediana(fig, axs, df, metrics, title="mediana"):
    fig.suptitle(title)
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        subplot_i = 0
        for metric in metrics:
            avg_series = median_df[metric]
            axs[subplot_i].plot(median_df.index, avg_series)
            axs[subplot_i].set_title(metric, fontsize=5)
            # axs[subplot_i].semilogy(base=10)
            subplot_i += 1     
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_bandas_mad(fig, axs, df, metrics, title ="bandas_mad"):
    fig.suptitle(title)
    grouped_block = df.groupby(block_vars)
    for (blockName), block_group in grouped_block:
        median_df = block_group.groupby("x_axis").median()
        mad_df = block_group.groupby("x_axis").mad()
        subplot_i = 0
        for metric in metrics:
            avg_series = median_df[metric]
            mad_series = mad_df[metric]
            axs[subplot_i].fill_between(x=median_df.index,
                        y1=avg_series - mad_series,
                        y2=avg_series + mad_series,
                        alpha=0.25
                        )
            axs[subplot_i].set_title(metric, fontsize=5)
            subplot_i += 1  
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

figure_offset = 0
title = "sujetos"
plot_sujetos(df, metrics, figure_offset, title=title, showLabel=True)
print(f"Listo {title}")

figure_offset = len(metrics)
title = "promedio_y_bandas_std"
plot_promedio(df, metrics, figure_offset, title=title)
plot_bandas_std(df, metrics, figure_offset, title=title)
print(f"Listo {title}")

figure_offset = len(metrics) * 2
title = "promedio_y_sujetos"
plot_promedio(df, metrics, figure_offset, title=title)
plot_sujetos(df, metrics, figure_offset, title=title, color_choice = 'grey', alpha=0.25)
print(f"Listo {title}")

figure_offset = len(metrics) * 3
title = "promedio_sujetos_y_bandas_std"
plot_promedio(df, metrics, figure_offset, title=title)
plot_sujetos(df, metrics, figure_offset, title=title, color_choice = 'grey', alpha=0.25)
plot_bandas_std(df, metrics, figure_offset, title=title)
print(f"Listo {title}")

figure_offset = len(metrics) * 4
title = "promedio_sujetos_y_bandas_sem"
plot_promedio(df, metrics, figure_offset, title=title)
plot_sujetos(df, metrics, figure_offset, title=title, color_choice = 'grey', alpha=0.25)
plot_bandas_sem(df, metrics, figure_offset, title=title)
print(f"Listo {title}")

figure_offset = len(metrics) * 5
title = "mediana_sujetos_y_bandas_sem"
plot_mediana(df, metrics, figure_offset, title=title)
plot_sujetos(df, metrics, figure_offset, title=title, color_choice = 'grey', alpha=0.25)
plot_bandas_mad(df, metrics, figure_offset, title=title)
print(f"Listo {title}")


metrics = [
    'area_error',
    'area_error_abs',
    'd',
    'temporal_error',
    'velocidad_media'
]
df['velocidad_media'] = df['d'] / df['reproduced_period']

def create_axs(metrics):
    fig, axs = plt.subplots(len(metrics), 1, sharex=True, constrained_layout=True)

    for ax in axs.flat:
            plt.setp(ax.get_xticklabels(), fontsize=5)
            plt.setp(ax.get_yticklabels(), fontsize=5)
    return fig, axs

title = "Summary_sujetos_promedio"
fig, axs = create_axs(metrics)
axs_plot_sujetos(fig, axs, df, metrics, title=title, color_choice = 'grey', alpha=0.25)
axs_plot_promedio(fig, axs, df, metrics, title=title)
print(f"Listo {title}")


title = "Summary_promedio_bandas_sem"
fig, axs = create_axs(metrics)
axs_plot_bandas_sem(fig, axs, df, metrics, title=title)
axs_plot_promedio(fig, axs, df, metrics, title=title)
print(f"Listo {title}")

title = "Summary_mediana_sujetos"
fig, axs = create_axs(metrics)
axs_plot_sujetos(fig, axs, df, metrics, title=title, color_choice = 'grey', alpha=0.25)
axs_plot_mediana(fig, axs, df, metrics, title=title)
print(f"Listo {title}")

title = "Summary_mediana_banda_mad"
fig, axs = create_axs(metrics)
axs_plot_bandas_mad(fig, axs, df, metrics, title=title)
axs_plot_mediana(fig, axs, df, metrics, title=title)
print(f"Listo {title}")

title = "Summary_mediana"
fig, axs = create_axs(metrics)
axs_plot_mediana(fig, axs, df, metrics, title=title)
print(f"Listo {title}")
# plt.show()

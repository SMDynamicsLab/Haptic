import os 
import pandas as pd
import matplotlib.pyplot as plt
from analisis_datos import * 
import numpy as np

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

# Todos los sujetos en un grafico
def plot_sujetos(df, metrics, figure_offset, title="", color_choice = None, alpha=1): 
    colors = ['pink',"b","g","r","c","m","y","k","w", "brown"]
    color_i = 0
    grouped_sujeto = df.groupby("sujeto")
    for sujeto, group_sujeto in grouped_sujeto:
        if not color_choice:
            color = colors[color_i]
            print(f"sujeto= {sujeto}, color = {color}")
        else:
            color = color_choice
        grouped_block = group_sujeto.groupby(block_vars)
        for (vmr, blockN, sound, force_type), block_group in grouped_block:
            figure_i = 1
            for metric in metrics:
                plt.figure(figure_offset + figure_i)
                plt.plot(block_group.trialSuccessN, block_group[metric],color=color, alpha=alpha)
                plt.title(metric + f" {title}")
                plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
                figure_i += 1
        color_i+=1

def plot_promedio(df, metrics, figure_offset, title="promedio"):
    mean_df = df.groupby("trialSuccessN").mean()
    figure_i = 1
    for metric in metrics:
        plt.figure(figure_offset + figure_i)
        avg_series = mean_df[metric]
        plt.plot(np.arange(len(avg_series)), avg_series)
        plt.title(metric + f" {title}")
        plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
        figure_i += 1     

def plot_bandas_std(df, metrics, figure_offset, title ="bandas_std"):
    mean_df = df.groupby("trialSuccessN").mean()
    std_df = df.groupby("trialSuccessN").std()
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
    mean_df = df.groupby("trialSuccessN").mean()
    sem_df = df.groupby("trialSuccessN").sem()
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
    median_df = df.groupby("trialSuccessN").median()
    figure_i = 1
    for metric in metrics:
        plt.figure(figure_offset + figure_i)
        avg_series = median_df[metric]
        plt.plot(np.arange(len(avg_series)), avg_series)
        plt.title(metric + f" {title}")
        plt.savefig(os.path.join(path, f"{metric}_{title}.png") , dpi = 300)
        figure_i += 1     

def plot_bandas_mad(df, metrics, figure_offset, title ="bandas_mad"):
    median_df = df.groupby("trialSuccessN").median()
    mad_df = df.groupby("trialSuccessN").mad()
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
    colors = ['pink',"b","g","r","c","m","y","k","w", "brown"]
    color_i = 0
    grouped_sujeto = df.groupby("sujeto")
    for sujeto, group_sujeto in grouped_sujeto:
        if not color_choice:
            color = colors[color_i]
            print(f"sujeto= {sujeto}, color = {color}")
        else:
            color = color_choice
        grouped_block = group_sujeto.groupby(block_vars)
        for (vmr, blockN, sound, force_type), block_group in grouped_block:
            subplot_i = 0
            for metric in metrics:
                axs[subplot_i].plot(block_group.trialSuccessN, block_group[metric],color=color, alpha=alpha)
                axs[subplot_i].set_title(metric, fontsize=5)
                subplot_i += 1
                
        color_i+=1
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_promedio(fig, axs, df, metrics, title="promedio"):
    fig.suptitle(title)
    mean_df = df.groupby("trialSuccessN").mean()
    subplot_i = 0
    for metric in metrics:
        avg_series = mean_df[metric]
        axs[subplot_i].plot((mean_df.index), avg_series)
        axs[subplot_i].set_title(metric, fontsize=5)
        subplot_i += 1     
        
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_bandas_std(fig, axs, df, metrics, title ="bandas_std"):
    fig.suptitle(title)
    mean_df = df.groupby("trialSuccessN").mean()
    std_df = df.groupby("trialSuccessN").std()
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
    mean_df = df.groupby("trialSuccessN").mean()
    sem_df = df.groupby("trialSuccessN").sem()
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
    median_df = df.groupby("trialSuccessN").median()
    subplot_i = 0
    for metric in metrics:
        avg_series = median_df[metric]
        axs[subplot_i].plot(np.arange(len(avg_series)), avg_series)
        axs[subplot_i].set_title(metric, fontsize=5)
        # axs[subplot_i].semilogy(base=10)
        subplot_i += 1     
    plt.savefig(os.path.join(path, f"{title}.png") , dpi = 500)

def axs_plot_bandas_mad(fig, axs, df, metrics, title ="bandas_mad"):
    fig.suptitle(title)
    median_df = df.groupby("trialSuccessN").median()
    mad_df = df.groupby("trialSuccessN").mad()
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
plot_sujetos(df, metrics, figure_offset, title=title)
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
axs_plot_promedio(fig, axs, df, metrics, title=title)
axs_plot_bandas_sem(fig, axs, df, metrics, title=title)
print(f"Listo {title}")

title = "Summary_mediana_sujetos"
fig, axs = create_axs(metrics)
axs_plot_mediana(fig, axs, df, metrics, title=title)
axs_plot_sujetos(fig, axs, df, metrics, title=title, color_choice = 'grey', alpha=0.25)
print(f"Listo {title}")

title = "Summary_mediana_banda_mad"
fig, axs = create_axs(metrics)
axs_plot_mediana(fig, axs, df, metrics, title=title)
axs_plot_bandas_mad(fig, axs, df, metrics, title=title)
print(f"Listo {title}")

title = "Summary_mediana"
fig, axs = create_axs(metrics)
axs_plot_mediana(fig, axs, df, metrics, title=title)
print(f"Listo {title}")
# plt.show()

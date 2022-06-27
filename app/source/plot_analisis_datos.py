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

def plot_bandas(df, metrics, figure_offset, title ="bandas"):
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

figure_offset = 0
title = "sujetos"
plot_sujetos(df, metrics, figure_offset, title)
print(f"Listo {title}")

figure_offset = len(metrics)
title = "promedio_y_bandas"
plot_promedio(df, metrics, figure_offset, title)
plot_bandas(df, metrics, figure_offset, title)
print(f"Listo {title}")

figure_offset = len(metrics) * 2
title = "promedio_y_sujetos"
plot_promedio(df, metrics, figure_offset, title)
plot_sujetos(df, metrics, figure_offset, title, color_choice = 'grey', alpha=0.25)
print(f"Listo {title}")

figure_offset = len(metrics) * 2
title = "promedio_sujetos_y_bandas"
plot_bandas(df, metrics, figure_offset, title)
print(f"Listo {title}")

# plt.show()

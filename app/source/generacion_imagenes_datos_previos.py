import os 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import cm
from plot.plot import plot
import time

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
plt.style.use('tableau-colorblind10')


plot_dir = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/Imagenes'

###################
start_time = time.time()
last_time = start_time
print("Comienzo generacion imagenes datos previos")

def plot_stats(title, last_time):
    t1 = last_time
    t2 = time.time()
    dt = t2-t1
    print(f"Finalizado grafico: {title} ({round(dt//60)}m{round(dt%60)}s)")
    return t2

def imagenes_datos_previos_1(datos_path, datos_file):
    plot_file = os.path.join(plot_dir,"Datos_previos_1_"+datos_file.replace(".csv", ".pdf"))
    metrics_count = 5
    subplot_params = {
        'figsize': [2*3,7],
        'gridspec_kw': {'height_ratios': [2] + [1]*(metrics_count-1)}
    }
    plot(
        output_file=os.path.join(datos_path, datos_file),
        plot_file=plot_file,
        fontsize=8,
        subplot_params=subplot_params,
        blockNames = ["Bloque 1: Linea de base", "Bloque 2: Perturbación", "Bloque 3: AfterEffects"],
        )
    plt.close()

def imagenes_datos_previos_2(datos_path, datos_file, datos_file_summary, force_count=6, name='Datos_previos_2'):
    metrics_count = 3
    subplot_params = {
        'figsize': [3, 3],
        'gridspec_kw': {'height_ratios': [2] + [1]*(metrics_count-1)}
    }
    blockNames = ["Perturbación", "AfterEffects"]
    plot_d_and_vel, plot_temp_err = False, False
    for i in range(force_count):
        block_filter = [2*i+1, 2*i+2]
        plot_file = os.path.join(plot_dir,f"{name}_fuerza{i+1}_"+datos_file.replace(".csv", ".pdf"))
        blockNames_i = [f'Bloque {block_filter[i]+1}:\n'+blockNames[i] for i in range(len(blockNames))]
        plot(
            output_file=os.path.join(datos_path, datos_file),
            plot_file=plot_file,
            file_summary=os.path.join(datos_path, datos_file_summary),
            fontsize=5,
            subplot_params=subplot_params,
            block_filter=block_filter,
            blockNames=blockNames_i,
            plot_d_and_vel=plot_d_and_vel,
            plot_temp_err=plot_temp_err,
            )
        plt.close()

def error_temporal(datos_path, datos_file_summary, name='Datos_previos_2'):
    fig, ax = plt.subplots(1,1)
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
    df_summary = pd.read_csv(os.path.join(datos_path, datos_file_summary), names=columns_summary, index_col=False)
    df_summary = df_summary[df_summary.trialSuccess == 1]
    df_summary['temporal_error'] = (df_summary['second_beep'] - df_summary['first_beep']) - df_summary['period']
    grouped_block = df_summary.groupby(['blockN', 'force_type'])
    for (blockN, force_type), block_group in grouped_block:
        block_group = block_group[block_group.trialSuccess == 1]
        if force_type:
            ax.plot(block_group.trial, block_group.temporal_error, label=f"Perturbación fuerza {force_type}")
            ax.scatter(block_group.trial, block_group.temporal_error, s=5)       
        elif blockN==0:
            ax.plot(block_group.trial, block_group.temporal_error, color='k', label="Sin perturbación")
            ax.scatter(block_group.trial, block_group.temporal_error, color='k', s=5)
        else:
            ax.plot(block_group.trial, block_group.temporal_error, color='k')
            ax.scatter(block_group.trial, block_group.temporal_error, color='k', s=5)
        ax.axhline(0, color='k', ls='dashed')
        ax.set_ylabel("Error temporal [ms]")
        ax.set_xlabel("Número de trial")
    plt.legend(loc="best")
    plot_file = os.path.join(plot_dir,f"{name}_temporal_error_"+datos_file.replace(".csv", ".pdf"))
    plt.savefig(plot_file)
    plt.close()

def periodo_reproducido_vmr(datos_path, datos_file_summary, name='Datos_previos_4'):
    fig, ax = plt.subplots(1,1)
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
    df_summary = pd.read_csv(os.path.join(datos_path, datos_file_summary), names=columns_summary, index_col=False)
    df_summary = df_summary[df_summary.trialSuccess == 1]
    df_summary['periodo_reproducido'] = df_summary['second_beep'] - df_summary['first_beep']
    grouped_block = df_summary.groupby(['blockN', 'period', 'vmr'])
    for (blockN, period, vmr), block_group in grouped_block:
        ax.plot(block_group.trial, [period]*len(block_group.trial), color='r', linestyle='dashed')
        if vmr and blockN==1:
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='b', label=f"Perturbación VMR")
        if vmr:
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='b')
            ax.scatter(block_group.trial, block_group.periodo_reproducido, color='b', s=5)            
        elif blockN==0:
            ax.plot(block_group.trial, [period]*len(block_group.trial), color='r', linestyle='dashed', label='Intervalo escuchado')
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='k', label="Sin perturbación")
            ax.scatter(block_group.trial, block_group.periodo_reproducido, color='k', s=5)
        else:
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='k')
            ax.scatter(block_group.trial, block_group.periodo_reproducido, color='k', s=5)
        ax.set_ylabel("Intervalo reproducido [ms]")
        ax.set_xlabel("Número de trial")
    plt.legend(loc="best")
    plot_file = os.path.join(plot_dir,f"{name}_periodo_reproducido_"+datos_file.replace(".csv", ".pdf"))
    plt.savefig(plot_file)
    plt.close()



def imagenes_datos_previos_4(datos_path, datos_file, datos_file_summary, name='Datos_previos_4'):
    metrics_count = 3
    subplot_params = {
        'figsize': [4, 3],
        'gridspec_kw': {'height_ratios': [2] + [1]*(metrics_count-1)}
    }
    plot_d_and_vel, plot_temp_err = False, False

    blockNames = ["Perturbación VMR 1", "Perturbación VMR 2", "Perturbación VMR 3"]
    block_filter = [1, 4, 7]
    blockNames_i = [f'Bloque {block_filter[i]+1}:\n'+blockNames[i] for i in range(len(blockNames))]
    plot_file = os.path.join(plot_dir,f"{name}a_vmr_perturbacion_"+datos_file.replace(".csv", ".pdf"))

    plot(
        output_file=os.path.join(datos_path, datos_file),
        plot_file=plot_file,
        file_summary=os.path.join(datos_path, datos_file_summary),
        fontsize=5,
        subplot_params=subplot_params,
        block_filter=block_filter,
        blockNames=blockNames_i,
        plot_d_and_vel=plot_d_and_vel,
        plot_temp_err=plot_temp_err,
        )
    plt.close()


    blockNames = ["AfterEffects VMR 1", "AfterEffects VMR 2", "AfterEffects VMR 3"]
    block_filter = [2, 5, 8]
    blockNames_i = [f'Bloque {block_filter[i]+1}:\n'+blockNames[i] for i in range(len(blockNames))]
    plot_file = os.path.join(plot_dir,f"{name}b_vmr_aftereffects_"+datos_file.replace(".csv", ".pdf"))
    plot(
        output_file=os.path.join(datos_path, datos_file),
        plot_file=plot_file,
        file_summary=os.path.join(datos_path, datos_file_summary),
        fontsize=5,
        subplot_params=subplot_params,
        block_filter=block_filter,
        blockNames=blockNames_i,
        plot_d_and_vel=plot_d_and_vel,
        plot_temp_err=plot_temp_err,
        )
    plt.close()

def periodo_reproducido_fuerza(datos_path, datos_file_summary, name='Datos_previos_5'):
    fig, ax = plt.subplots(1,1)
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
    df_summary = pd.read_csv(os.path.join(datos_path, datos_file_summary), names=columns_summary, index_col=False)
    df_summary = df_summary[df_summary.trialSuccess == 1]
    df_summary['periodo_reproducido'] = df_summary['second_beep'] - df_summary['first_beep']
    grouped_block = df_summary.groupby(['blockN', 'period', 'force_type'])
    for (blockN, period, force_type), block_group in grouped_block:
        ax.plot(block_group.trial, [period]*len(block_group.trial), color='r', linestyle='dashed')
        if force_type and blockN==1:
            print(force_type and blockN==1)
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='b', label=f"Perturbación fuerza {force_type}")
        if force_type:
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='b')
            ax.scatter(block_group.trial, block_group.periodo_reproducido, color='b', s=5)            
        elif blockN==0:
            ax.plot(block_group.trial, [period]*len(block_group.trial), color='r', linestyle='dashed', label='Intervalo escuchado')
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='k', label="Sin perturbación")
            ax.scatter(block_group.trial, block_group.periodo_reproducido, color='k', s=5)
        else:
            ax.plot(block_group.trial, block_group.periodo_reproducido, color='k')
            ax.scatter(block_group.trial, block_group.periodo_reproducido, color='k', s=5)
        ax.set_ylabel("Intervalo reproducido [ms]")
        ax.set_xlabel("Número de trial")
    plt.legend(loc="best")
    plot_file = os.path.join(plot_dir,f"{name}_periodo_reproducido_"+datos_file.replace(".csv", ".pdf"))
    plt.savefig(plot_file)
    plt.close()

def imagenes_datos_previos_5(datos_path, datos_file, datos_file_summary, name='Datos_previos_5'):
    metrics_count = 3
    subplot_params = {
        'figsize': [4, 4],
        'gridspec_kw': {'height_ratios': [2] + [1]*(metrics_count-1)}
    }
    plot_d_and_vel, plot_temp_err = False, False

    blockNames = ["Perturbación", "AfterEffects", "Perturbación", "AfterEffects"]
    block_filter = [1, 2, 4, 5]
    blockNames_i = [f'Bloque {block_filter[i]+1}:\n'+blockNames[i] for i in range(len(blockNames))]
    plot_file = os.path.join(plot_dir,f"{name}a_fuerza_"+datos_file.replace(".csv", ".pdf"))
    plot(
        output_file=os.path.join(datos_path, datos_file),
        plot_file=plot_file,
        file_summary=os.path.join(datos_path, datos_file_summary),
        fontsize=5,
        subplot_params=subplot_params,
        block_filter=block_filter,
        blockNames=blockNames_i,
        plot_d_and_vel=plot_d_and_vel,
        plot_temp_err=plot_temp_err
        )
    plt.close()


datos_path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/2. Datos vmr sabrina/'
datos_file = 'v_sabrinalopez_e_2021_12_04_21_10_26_out.csv'
imagenes_datos_previos_1(datos_path, datos_file)
last_time = plot_stats('datos 1', last_time)

datos_path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/3. Datos ft con y sin feedback Nicodg'
datos_file = 'ft_nicodg_e_2022_05_12_21_53_06_out.csv'
datos_file_summary = 'ft_nicodg_e_2022_05_12_21_53_06_out.csvtimes-summary'
imagenes_datos_previos_2(datos_path, datos_file, datos_file_summary, force_count=6, name='Datos_previos_2')
error_temporal(datos_path, datos_file_summary, name='Datos_previos_2')
last_time = plot_stats('datos 2', last_time)

datos_path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/3. Datos ft con y sin feedback Nicodg'
datos_file = 'ft_nicodg_sinfeedback_e_2022_05_17_22_03_53_out.csv'
datos_file_summary = 'ft_nicodg_sinfeedback_e_2022_05_17_22_03_53_out.csvtimes-summary'
imagenes_datos_previos_2(datos_path, datos_file, datos_file_summary, force_count=4, name='Datos_previos_3')
error_temporal(datos_path, datos_file_summary, name='Datos_previos_3')
last_time = plot_stats('datos 3', last_time)

datos_path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/4. Datos vt sin feedback Nicodg'
datos_file = 'vt_nicodg_e_2022_05_26_00_45_10_out.csv'
datos_file_summary = 'vt_nicodg_e_2022_05_26_00_45_10_out-times-summary.csv'
imagenes_datos_previos_4(datos_path, datos_file, datos_file_summary, name='Datos_previos_4')
periodo_reproducido_vmr(datos_path, datos_file_summary, name='Datos_previos_4c')
last_time = plot_stats('datos 4', last_time)

datos_path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/5. Datos ft 2 periodos sin feedback Nicodg'
datos_file = 'ft_nicodg_e_2022_06_01_23_29_03_out.csv'
datos_file_summary = 'ft_nicodg_e_2022_06_01_23_29_03_out-times-summary.csv'
periodo_reproducido_fuerza(datos_path, datos_file_summary, name='Datos_previos_5')
imagenes_datos_previos_5(datos_path, datos_file, datos_file_summary, name='Datos_previos_5')
last_time = plot_stats('datos 5', last_time)

datos_path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/6. Datos rodri ft 2 periodos'
datos_file = 'ft_rodrilaje_e_2022_06_02_14_39_46_out.csv'
datos_file_summary = 'ft_rodrilaje_e_2022_06_02_14_39_46_out-times-summary.csv'
periodo_reproducido_fuerza(datos_path, datos_file_summary, name='Datos_previos_6')
imagenes_datos_previos_5(datos_path, datos_file, datos_file_summary, name='Datos_previos_6')
last_time = plot_stats('datos 6', last_time)



'''
1. sacar eje veritcal de todos menos el ultimo y el primero 

'''


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Finalizado en {elapsed_time // 60} minutos y {elapsed_time % 60} segundos")
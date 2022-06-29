import os 
import pandas as pd
from plot.plot_error import calculate_error_area
from plot.distance import distance
path = "/home/Carolina/Documents/Personal/Tesis/Haptic/app/data/Datos vft"
files_dict = {
    "vft_agusbarreto": {
        "path": "vft_agusbarreto_",
        "file": "vft_agusbarreto_e_2022_06_23_09_33_48_out.csv"
        },
    "vft_ayelensantos": {
        "path": "vft_ayelensantos_",
        "file": "vft_ayelensantos_e_2022_06_23_10_34_04_out.csv"
        },
    "vft_caro": {
        "path": "vft_caro_",
        "file": "vft_caro_e_2022_06_17_17_03_21_out.csv"
        },
    "vft_constanza": {
        "path": "vft_constanza_",
        "file": "vft_constanza_e_2022_06_23_11_39_07_out.csv"
        },
    "vft_gabrielgoren": {
        "path": "vft_gabrielgoren_",
        "file": "vft_gabrielgoren_e_2022_06_23_15_04_55_out.csv"
        },
    "vft_hilariob": {
        "path": "vft_hilariob_",
        "file": "vft_hilariob_e_2022_06_23_14_36_28_out.csv"
        },
    "vft_luciabusolini": {
        "path": "vft_luciabusolini_",
        "file": "vft_luciabusolini_e_2022_06_23_12_09_14_out.csv"
        },
    "vft_matiasherrera": {
        "path": "vft_matiasherrera_",
        "file": "vft_matiasherrera_e_2022_06_23_13_17_49_out.csv"
        },
    "vft_melisavinograd": {
        "path": "vft_melisavinograd_",
        "file": "vft_melisavinograd_e_2022_06_23_14_07_23_out.csv"
        },
    "vft_yamila": {
        "path": "vft_yamila_",
        "file": "vft_yamila_e_2022_06_23_11_02_47_out.csv"
        },
}

columns = [
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

trial_vars = ['trial', 'angle', 'trialSuccess']
block_vars = ['vmr', 'blockN', 'sound', 'force_type']

def analisis_datos():
    for sujeto in files_dict:
        # Add files info to dict
        file = files_dict[sujeto]["file"]
        file_summary = file.replace(".csv", "-times-summary.csv")
        files_dict[sujeto]["file_summary"] = files_dict[sujeto]["file"].replace(".csv", "-times-summary.csv")
        
        # Create paths
        file_path = os.path.join(path, files_dict[sujeto]["path"])
        files_dict[sujeto]["file_path"] = file_path
        file = os.path.join(file_path, file)
        file_summary = os.path.join(file_path, file_summary)
        
        # Read csvs
        df = pd.read_csv(file, names=columns, index_col=False)
        df_summary = pd.read_csv(file_summary, names=columns_summary, index_col=False)
        
        # Add metadata about subject
        df["sujeto"] = sujeto
        df_summary["sujeto"] = sujeto

        # Add successful trial number to df_summary
        df_summary.sort_values(by=['trial'], inplace=True)
        df_summary.loc[df_summary.trialSuccess == 1, 'trialSuccessN'] = [i+1 for i in range(len(df_summary[df_summary.trialSuccess == 1]))]
        df_summary.loc[df_summary.trialSuccess == 0, 'trialSuccessN'] = 0
        df_summary.trialSuccessN = df_summary.trialSuccessN.astype(int)

        # Calculate metrics
        grouped_block = df.groupby(block_vars)
        for (vmr, blockN, sound, force_type), block_group in grouped_block:
            block_group = block_group[block_group.trialSuccess == 1]
            grouped_trial = block_group.groupby(trial_vars)
            for (trial, angle, trialSuccess), group in grouped_trial:
                print(f"sujeto {sujeto}, block {blockN}, trial {trial}, trialSuccessN {df_summary[df_summary.trial == trial].trialSuccessN.values[0]}")

                # Keep only time between beeps
                first_beep = float(df_summary.loc[df_summary.trial == trial, "first_beep"])
                second_beep = float(df_summary.loc[df_summary.trial == trial, "second_beep"])
                group.drop(group[group['timeMs'] < first_beep].index, inplace = True)
                group.drop(group[group['timeMs'] > second_beep].index, inplace = True)
                
                # Calculate area errors
                area_error, area_error_abs = calculate_error_area(group, angle)
                df_summary.loc[df_summary.trial == trial, "area_error"] = area_error
                df_summary.loc[df_summary.trial == trial, "area_error_abs"] = area_error_abs
                
                # Calculate distance
                d = distance(group)
                df_summary.loc[df_summary.trial == trial, "d"] = d
                
                # Calculate temporal metrics
                first_beep = df_summary[df_summary.trial == trial]['first_beep']
                second_beep = df_summary[df_summary.trial == trial]['second_beep']
                period = df_summary[df_summary.trial == trial]['period']
                reproduced_period = second_beep - first_beep
                temporal_error = period - reproduced_period
                df_summary.loc[df_summary.trial == trial, "reproduced_period"] = reproduced_period
                df_summary.loc[df_summary.trial == trial, "temporal_error"] = temporal_error

        # Save df to dict
        files_dict[sujeto]["file_df"] = df
        files_dict[sujeto]["file_summary_df"] = df_summary


if __name__ == "__main__":
    analisis_datos()
    vertical_concat = pd.DataFrame()
    
    for sujeto in files_dict:
        file_path = files_dict[sujeto]["file_path"]
        file_analisis = files_dict[sujeto]["file"].replace(".csv", "-analisis.csv")
        file_analisis = os.path.join(file_path, file_analisis)
        print(f"Output file is {file_analisis}")
        files_dict[sujeto]["file_summary_df"].to_csv(file_analisis,index=False)
        vertical_concat = pd.concat([vertical_concat, files_dict[sujeto]["file_summary_df"]], axis=0)

    vertical_concat.to_csv(os.path.join(path, "Merge_analisis.csv"),index=False)  

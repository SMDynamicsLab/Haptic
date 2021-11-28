import numpy as np
import pandas as pd 




def distance(data):
    df = data.reset_index(drop=True)
    p1 = df.iloc[:-1]
    p2 = df.iloc[1:]
    p2 = p2.reset_index(drop=True)
    ds = p2 - p1 
    d = np.sqrt(ds.x ** 2 + ds.y ** 2)
    return d.sum()

def total_distance(data):
    df = data.reset_index(drop=True)
    last_index = len(df)
    p1 = df.iloc[0]
    p2 = df.iloc[-1]
    ds = p2 - p1
    d = np.sqrt(ds.x ** 2 + ds.y ** 2)
    return d


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/out_20211022212151_ESTE.csv'
    names = ['trial', 'x', 'y', 'z']
    var_names = ['angle', 'vmr', 'blockN']
    names += var_names
    df = pd.read_csv(output_file, names=names, index_col=False)
    df['x'] = -df['x']*100
    df['y'] = df['y']*100

    block_count = len(df.blockN.unique())
    fig, axs = plt.subplots(1,block_count, sharey=True)
    fig.tight_layout()

    grouped = df.groupby(['trial','blockN', 'vmr'])

    for (trial, blockN, vmr), group in grouped:
        d = distance(group)
        i = total_distance(group)
        print(f'trial:{trial} block:{blockN} distance:{d} i:{i}')
        axs[blockN].scatter(trial,d)


    plt.show()


    


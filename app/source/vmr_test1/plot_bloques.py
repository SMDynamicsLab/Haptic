import pandas as pd
import matplotlib.pyplot as plt

output_file = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/vmr_test1/resultados/out_20211022212151_ESTE.csv'
names = ['trial', 'x', 'y', 'z']
var_names = ['angle', 'vmr', 'blockN']
names += var_names
df = pd.read_csv(output_file, names=names, index_col=False)
df['x'] = -df['x']*100
df['y'] = df['y']*100
block_count = len(df.blockN.unique())
fig, axs = plt.subplots(1, block_count, sharey=True)
fig.tight_layout()
grouped = df.groupby(['trial', 'blockN', 'vmr'])

for ax in axs:
    ax.axis('equal')
    ax.set_box_aspect(1)

for (trial, blockN, vmr), group in grouped:
    group.plot(x='y', y='x', ax=axs[blockN], label=f'trial {trial}', legend=False)

for (blockN, vmr), group in df.groupby(['blockN', 'vmr']):
    trial_count = len(group.trial.unique())
    axs[blockN].set_title(f'vmr: {vmr} trials: {trial_count}')

plt.show()

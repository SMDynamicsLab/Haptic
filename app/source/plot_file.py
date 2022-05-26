from zipfile import ZipFile
import os
from plot.plot import plot

path = '/home/Carolina/Documents/Personal/Tesis/Haptic/app/source/../data/vt_nicodg_e_2022_05_26_00_45_10.zip'
archive = ZipFile(path, 'r')
file = archive.infolist()[0].filename
archive.extract(file)

plot(file)

if os.path.exists(file):
    os.remove(file)
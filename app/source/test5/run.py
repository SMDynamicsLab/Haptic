import os
import subprocess
import pathlib
import time
import sys
status, output = subprocess.getstatusoutput('make')
if status != 0:
    print(output)

data_path = os.path.join(sys.path[0], 'data')
os.makedirs(data_path, exist_ok=True)

input = os.path.join(data_path, 'in.csv')
output = os.path.join(data_path, 'out.csv')

# agregar chequeo sobre si existe
fname = pathlib.Path(input)
input_mod_time = fname.stat().st_mtime # epoch float

bin_file = os.path.join( sys.path[0], '../../bin/lin-x86_64/test5')
subprocess.Popen([
    bin_file, 
    input, 
    output
    ]
    # , stdout=subprocess.DEVNULL #para evitar que salga a consola
    )

# Consumo de memoria/CPU: htop -p "$(pgrep -d , "python|test")"
while True:
    # no sleep 99% CPU
    # time.sleep(0.001) #~9% CPU
    time.sleep(0.01) # ~2% CPU
    if input_mod_time != fname.stat().st_mtime:
        print('file changed')
        input_mod_time = fname.stat().st_mtime


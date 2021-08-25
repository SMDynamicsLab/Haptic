import os
import subprocess

status, output = subprocess.getstatusoutput('make')
if status != 0:
    print(output)

data_path = os.path.join(os.getcwd(), 'data')
os.makedirs(f'{data_path}', exist_ok=True)
input, output = 'in.csv', 'out.csv'
subprocess.Popen([
    '../../bin/lin-x86_64/test5', 
    os.path.join(data_path, input), 
    os.path.join(data_path, output)
    ]
    # , stdout=subprocess.DEVNULL #para evitar que salga a consola
    )


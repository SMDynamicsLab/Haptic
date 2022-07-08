from analisis_datos import *
from plot.plot import plot

# Plot para cada sujeto
for sujeto in files_dict:
    print(f"Sujeto: {sujeto}")
    file_path = os.path.join(path, files_dict[sujeto]["path"])
    file = files_dict[sujeto]["file"]
    file = os.path.join(file_path, file)
    file_summary = file.replace(".csv", "-times-summary.csv")
    plot_file = file.replace("_out.csv", "_plot.png")
    plot(file, plot_file, file_summary=file_summary)

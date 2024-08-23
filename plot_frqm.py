import os
import numpy as np
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt



def type1(df, label_idx, number, refresh_rate, bitrate, SAVE = False):
    """x axis is bandwidth, y axis is JOD, color is resolution"""
    # bandwidth_dict = {10.37349118: 32000, 9.680344: 16000, 8.98719682:8000}
    fig, ax = plt.subplots(figsize=(8, 5))

    # labels = ['360p', '480p', '720p', '864p', '1080p']
    labels = ['1080p']
    colors = ['red']
    # colors = ['blue', 'greenyellow', 'red', 'gray', 'cyan', 'green', 'orange',]

    # collect data for each resolution
    # manually skip the resolution we dont want
    resolution_not_want = ['540p']
    for i, resolution in enumerate(labels):
        print(f'\n\n\ni resolution {i, resolution}')
        if resolution in resolution_not_want:
            continue

        jod = []
        for num in range(0, number): # e.g. first 3 fps, i.e. 30, 60, 70
            val = df.iloc[label_idx, 1+i+5*num]
            jod.append(val)
        jod = [float(v) for v in jod]        
        # print(f'resolution {resolution}, jod {jod}, label {labels[i]}')
        ax.plot(refresh_rate, jod, marker='o', label=labels[i], linestyle='-', color=colors[i])

    ax.set_xlabel('Refresh rate (Hz)')
    ax.set_xticks(refresh_rate)
    ax.set_ylabel('JOD')
    ax.set_title(f'CVVDP results- path{path}_seg{seg}, speed {speed} - {bitrate} kbps')
    ax.grid(True)
    ax.legend()

    if SAVE:
        p1 = f'{scene_output_dir}/plot1'
        os.makedirs(p1, exist_ok=True)
        img_path = f"{p1}/p1_{scene_name}_{sheet_name}_{bitrate}.png"
        if not os.path.exists(img_path):
            fig.savefig(img_path)
            print(f"File saved: {img_path}")
        else:
            print(f"File already exists: {img_path}")
        # plt.savefig(f"{p1}/p1_{scene_name}_{sheet_name}_{bitrate}.png")
    if SHOW:
        plt.show()


def type2(df, label_idx, bitrate, number, refresh_rate, SAVE = False):
    """x axis is resolution, y axis is JOD, color is bitrate, labels are refresh rate"""
    x_values = np.array([1080, 864, 720, 480, 360,]) # resolution
    x_values = sorted(x_values)
    # print(f'\n\n\n')
    fig, ax = plt.subplots(figsize=(8, 5))
    for num in range(number): # loop column
        # cvvdp jod from file1
        jod_cvvdp = df.iloc[label_idx, 1+5*num:6+5*num].values
        jod_cvvdp = [float(v) for v in jod_cvvdp]        

        # print(f'idx {num}, fps{refresh_rate[num]}, JOD {jod_cvvdp}, ') # max JOD {max(jod_cvvdp)}
        max_jod_idx = np.argmax(jod_cvvdp)
        # print(f'idx {num}, fps{refresh_rate[num]}, JOD {jod_cvvdp}, max JOD {max(jod_cvvdp)}')
        max_jod.append(max(jod_cvvdp))
        max_res.append(x_values[max_jod_idx])

        ax.plot(x_values, jod_cvvdp, marker='o', label=f'{refresh_rate[num]} fps')
        ax.set_xticks(x_values)

    ax.set_xlabel('Resolution')
    ax.set_ylabel('JOD')
    ax.set_title(f'CVVDP results - path{path}_seg{seg}, speed {speed} - {bitrate} kbps')
    ax.grid(True)
    ax.legend()
    if SAVE:
        p2 = f'{scene_output_dir}/plot2'
        os.makedirs(p2, exist_ok=True)
        img_path = f"{p2}/p2_{scene_name}_{sheet_name}_{bitrate}.png"
        if not os.path.exists(img_path):
            fig.savefig(img_path)
            print(f"File saved: {img_path}")
        else:
            print(f"File already exists: {img_path}")
        # fig.savefig(f"{p2}/p2_{scene_name}_{sheet_name}_{bitrate}.png")
    if SHOW:
        plt.show()



# download cvvdp results from HPC
# process results by running this file
# write to excel using write_excel.py
# plot using plot_cvvdp.py

# suitable for excel written using program, e.g. suntemple-05-03, sheetname fast, with 30-120fps
# Plot cvvdp results from csv file
# in type 2 change 2+6*num:9+6*num to 2+7*num:9+7*num if has 676 column
if __name__ == "__main__":
    SAVE = True # True, False
    SHOW = False

    VRR_PLOT_HPC = r'C:\Users\15142\Projects\VRR\VRR_Plot_HPC'
    refresh_rate = [30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
    
    bitrate_dict = {500: 0, 1000: 1, 1500: 2, 2000: 3,}
    bitrates = [500, 1000, 1500, 2000]

    bitrate_dict = {400: 0, 700: 1, 900: 2}
    bitrates = [400, 700, 900]
    
    # bitrate_dict = {300: 0,}
    # bitrates = [300,]
    
    SCENES = ['bedroom', 'bistro', 'crytek_sponza', 'gallery', 'living_room', \
        'lost_empire', 'room', 'sibenik', 'suntemple', 'suntemple_statue']

    # SCENES = ['bedroom', 'crytek_sponza', 'gallery', 'living_room', 'lost_empire', 'room', 'sibenik', 'suntemple', 'suntemple_statue']
    # problem: living_room, suntemple, sibenik, room, gallery, crytek_sponza
    SCENES = ['bistro']
    excel_date = '2024-08-14'
    # excel_date = '2024-08-14_300kbps'
    
    for scene_name in SCENES:
        print(f'\n\n\n================================== SCENE {scene_name} ==================================')
        file_path = f'{VRR_PLOT_HPC}/data-{excel_date}/{scene_name}.xlsx'
        for path in range(1, 4):
            for seg in range(1, 4):
                for speed in range(1, 4):
                    if SAVE:
                        today = date.today()
                        scene_output_dir = f'{VRR_PLOT_HPC}/plot-{today}/{scene_name}'
                        os.makedirs(scene_output_dir, exist_ok=True)

                    sheet_name = f'path{path}_seg{seg}_{speed}'
                    df = pd.read_excel(file_path, sheet_name=sheet_name, na_values=['NA'])
                    print(f'============================ sheet_name {sheet_name} ============================')
                    for bitrate in bitrates:
                        # print(f'bitrate {bitrate}')
                        print(f'\n================= bitrate {bitrate} kbps =================')
                        max_jod = []
                        max_res = []
                        type1(df, bitrate_dict[bitrate], len(refresh_rate), refresh_rate, bitrate, SAVE)
                        type2(df, bitrate_dict[bitrate], bitrate, len(refresh_rate), refresh_rate, SAVE)
                        print(f'max_jod {max_jod}')
                        max_idx = np.argmax(max_jod) # only availble if type2 is run
                        # print(f'\nmax_res {max_res}')
                        print(f'bitrate {bitrate}, max JOD is {max_jod[max_idx]} with resolution {max_res[max_idx]} fps {refresh_rate[max_idx]}')

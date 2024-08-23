import os


def process_txt_single_scene(jobid_list, cleaned_scene_path):
    for jobid in jobid_list:
        print(f'===== jobid {jobid} =====')
        input_file_path = f'{input_scene_path}/{SCENE}_{jobid}.txt'
        output_file_path = f'{cleaned_scene_path}/{SCENE}_{jobid}.txt'

        if not os.path.exists(input_file_path):
            print(f"jobid {jobid}, input file {input_file_path} NOT exists, skip.")
            continue

        if os.path.exists(output_file_path):
            print(f"jobid {jobid}, output file {output_file_path} exists, skip.")
            continue

        with open(input_file_path, "r") as file:
            lines = file.readlines()

        filtered_lines = [line for line in lines if not line.strip().lower().startswith(('current', 'dec_file', 'ref_file', 'dist_fps', 'frames_resampled', 'num_frames_dist', 'make yuv'))]
        # filtered_lines = [line for line in lines if line.strip()]

        if PROCESS_TXT:
            with open(output_file_path, "w") as file:
                for line in filtered_lines:
                    if ("Command executed successfully." not in line) and line.strip():
                        file.write(line)



# download cvvdp results from HPC
# process results by running this file
# write to excel using write_excel.py
# plot using plot_cvvdp.py
if __name__ == "__main__":
    SCENES = ['bedroom', 'bistro', 'crytek_sponza', 'gallery', 'living_room', \
              'lost_empire', 'room', 'sibenik', 'suntemple', 'suntemple_statue']
    # SCENES = ['bedroom', 'living_room', 'lost_empire', 'room', 'suntemple', 'suntemple_statue']
    # SCENES = ['bistro', 'crytek_sponza', 'gallery', 'sibenik']
    SCENES = ['bistro'] # TODO
    DATA_DIR = "08-22"
    PROCESS_TXT = True # False True
    jobid_list = [i for i in range(1, 2)] # TODO

    for SCENE in SCENES:
        input_scene_path = f'{DATA_DIR}/{SCENE}'
        cleaned_scene_path = f'{DATA_DIR}/cleaned_{SCENE}'
        os.makedirs(cleaned_scene_path, exist_ok=True)
        process_txt_single_scene(jobid_list, cleaned_scene_path)
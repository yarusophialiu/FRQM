import os
from math import *


def count_files_in_subfolders(root_directory):
    # Traverse the directory tree starting from the root directory
    for root, dirs, files in os.walk(root_directory):
        print(f'dirs {dirs}')
        for dir_name in dirs:
            # Get the full path of the subfolder
            subfolder_path = os.path.join(root, dir_name)
            # Count the number of files in the subfolder
            file_count = sum([len(files) for _, _, files in os.walk(subfolder_path)])
            print(f"Subfolder: {subfolder_path}, File count: {file_count}")
            os.chdir(f'/home/yl962/rds/hpc-work/VRR/VRRMP4_CVVDP/crytek_sponza/{dirs}')
            current_directory = os.getcwd()
            print(f"Current working directory: {current_directory}")


def mapIdToPath(id):
    """
    NOTE: input id starts from 0 not 1, HPC job id starts from 1
    so should be mapIdToPath(JOBID-1)

    we run 15 jobs/tasks (allocate 13 gpus) at one time, each scene has 45 clips, so we run 3 times
    for each task id, we run videos for 1 scene, 1 seg, 1 speed, i.e. for loop 50 * 13 = 650 videos
    e.g. sbatch --array=0-14:1 -A STARS-SL3-GPU submission_script

    id is from 0-44, map id -> path, seg, speed

    e.g. id 0 -> paths[0], segs[0], speeds[0]
         id 1 -> paths[0], segs[0], speeds[1]
    Note that id in HPC starts from 1, so delete id by 1 when call the function
    mapIdToPath(0) -> (1, 1, 1) path1 seg1 speed1
    mapIdToPath(16) -> (2, 3, 2) path2 seg3 speed2
    """
    pathIdx = int(floor(id/9))
    segIdx = int(floor((id - pathIdx * 9) / 3))
    speedIdx = (id - pathIdx * 9) % 3
    paths = [1, 2, 3, 4, 5]
    segs = [1, 2, 3,]
    speeds = [1, 2, 3,]
    print(f'pathIdx {pathIdx}, segIdx {segIdx} speedIdx {speedIdx}')
    print(f'{paths[pathIdx], segs[segIdx], speeds[speedIdx]}')
    return paths[pathIdx], segs[segIdx], speeds[speedIdx]


def mapPathToId(path, seg, speed):
    """
    NOTE: output id starts from 0 not 1, HPC job id starts from 1
    """
    id = (path-1) * 9 + (seg-1) * 3 + speed - 1
    print(f'id {id}')
    return id

import os
import logging
from frqm_calc import *
from read_yuv import *
from math import *
import argparse


def mapIdToPath(id):
    """
    we run 15 jobs/tasks (allocate 13 gpus) at one time, each scene has 45 clips, so we run 3 times
    for each task id, we run videos for 1 scene, 1 seg, 1 speed, i.e. for loop 50 * 13 = 650 videos
    e.g. sbatch --array=0-14:1 -A STARS-SL3-GPU submission_script

    id is from 0-44, map id -> path, seg, speed

    e.g. id 0 -> paths[0], segs[0], speeds[0]
         id 1 -> paths[0], segs[0], speeds[1]
    """
    pathIdx = int(floor(id/9))
    segIdx = int(floor((id - pathIdx * 9) / 3))
    speedIdx = (id - pathIdx * 9) % 3
    paths = [1, 2, 3, 4, 5]
    segs = [1, 2, 3,]
    speeds = [1, 2, 3,]
#    print(f'pathIdx {pathIdx}, segIdx {segIdx} speedIdx {speedIdx}')
    return paths[pathIdx], segs[segIdx], speeds[speedIdx]



def calc_frqm(dist_path, ref_path, dec_yuv_path, ref_yuv_path):
    # print(f'enter calc_frqm')
    width = 1920
    height = 1080

    cap_dist = cv2.VideoCapture(dist_path)
    cap_ref = cv2.VideoCapture(ref_path)
    
    dist_fps = int(cap_dist.get(cv2.CAP_PROP_FPS))
    ref_fps = int(cap_ref.get(cv2.CAP_PROP_FPS))
    print(f'dist_fps {dist_fps}, ref_fps {ref_fps}')
    assert int(ref_fps) == int(reference_fps)


    num_frames_dist = int(cap_dist.get(cv2.CAP_PROP_FRAME_COUNT))
    num_frames_ref = int(cap_ref.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f'num_frames_dist {num_frames_dist}, num_frames_ref {num_frames_ref}')
    cap_dist.release()
    cap_ref.release()

    stream_dist = open(dec_yuv_path, 'rb') # frqm_dist.yuv data/test_15fps.yuv
    stream_ref = open(ref_yuv_path, 'rb') # frqm_ref.yuv data/test_60fps.yuv
    frames_hfr, frames_lfr = [], [] # high, low, i.e. ref dist

    for iFrame in range(num_frames_dist):
        frame_dist_y, _, _ = read_frame_yuv(stream_dist, width, height, iFrame, 8, pix_fmt='420')
        frames_lfr.append(frame_dist_y)
    
    for iFrame in range(num_frames_ref):
        frame_ref_y, _, _ = read_frame_yuv(stream_ref, width, height, iFrame, 8, pix_fmt='420')
        frames_hfr.append(frame_ref_y)
        
    stream_dist.close()
    stream_ref.close()

    # print(f'frames_lfr {np.array(frames_lfr).shape}') # frames_lfr -- shape (num_frames,H,W)
    frames_lfr_up = temporal_upsample(np.array(frames_lfr), dist_fps, ref_fps, num_frames_ref, ref_fps)
    # print(f'frames_lfr_up {frames_lfr_up.shape}')
    # print(f'frames_hfr {np.array(frames_lfr_up).shape}')

    frqm = compute_frqm(np.array(frames_hfr), np.array(frames_lfr_up), fps_h=ref_fps)

    # print(f'frqm {frqm}')
    print(f"FRQM={frqm:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('SLURM_ARRAY_TASK_ID', type=str, help='The id of task')
    parser.add_argument('scene', type=str, help='scene')
    args = parser.parse_args()
    id = args.SLURM_ARRAY_TASK_ID
    id = int(id)
    scene = args.scene 

    # id = 1

    id -= 1
    VRR = r'C:\Users\15142\Projects\VRR'
    VRRMP4 = f'{VRR}/VRRMP4/'
    VRRMP4_CVVDP = f'{VRR}/VRRMP4_CVVDP'
    reference_fps = 166


    # SCENES = ["bistro", "gallery", "crytek_sponza", "sibenik"]
    # scene = SCENES[id]
    scene = "bistro"
    print(f'scene {scene}')

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger()
    logger.info(f"SLURM_ARRAY_TASK_ID (renamed to id): {id}")

    path, seg, speed = mapIdToPath(id)
    base_dir = f'{VRRMP4_CVVDP}/{scene}/{scene}_path{path}_seg{seg}_{speed}'
    ref_file = f'{base_dir}/ref{reference_fps}_1080/refOutput.mp4'

    ref_yuv =  f'{base_dir}/ref{reference_fps}_1080/frqm_ref.yuv'
    if not os.path.exists(f'{ref_yuv}'):
        print(f'make yuv file {ref_yuv}')
        os.system('ffmpeg -hide_banner -loglevel error -i {} {}'.format(ref_file, ref_yuv))

    logger.info(f"path, seg, speed: {path, seg, speed}\n\n")
    logger.info(f'Scene: {scene}')
    logger.info(f"base_dir: {base_dir}")

    bitrates = [500, 1000, 1500, 2000]
    # bitrates = [500,]
    
    print(f'ref_file {ref_file}')

    for bitrate in bitrates:
        print(f'\n\n========================= bitrate {bitrate} =========================')
        logger.info(f'Processing video with bitrate: {bitrate}kbps')
        folder = os.path.join(f'{base_dir}', f'{bitrate}kbps')
        logging.info(f'folder {folder}')
        items = os.listdir(folder) # ['fps120', 'fps150',]
        items = sorted(items)
        logging.info(f'items {items}')
        # items = ['fps100'] # TODO: comment out

        for fps_name in items:
            print(f'\n\n========================= {fps_name} =========================')
            current_dir_path = os.path.join(folder, fps_name)
            print(f'current_dir_path {current_dir_path}')

            # e.g. dec30_1080
            dec_dirs = [f for f in os.listdir(current_dir_path)]
            dec_dirs = sorted(dec_dirs)
            logging.info(f'dec_files {dec_dirs}\n')
            for dec_folder in dec_dirs:
                if '1080' in dec_folder:
                    dec_dirs_full_path = os.path.join(current_dir_path, dec_folder)
                    dec_files = [f for f in os.listdir(dec_dirs_full_path)]
                    dec_file = f'{dec_dirs_full_path}/{dec_files[0]}'
                    print(f'dec_file {dec_file}\n')


                    # TODO: dist_path 
                    dec_yuv =  f'{dec_dirs_full_path}/frqm_dec.yuv'
                    if not os.path.exists(f'{dec_yuv}'):
                        # print(f'make yuv for decoded file {dec_yuv}\n')
                        os.system('ffmpeg -hide_banner -loglevel error -i {} {}'.format(dec_file, dec_yuv))
                    calc_frqm(dec_file, ref_file, dec_yuv, f'{ref_yuv}')
                    
                    # delete files, modify command accordingly
                    os.remove(f'{dec_yuv}')
    # os.remove(f'{ref_yuv}')





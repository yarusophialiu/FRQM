import os
from frqm_calc import *
from read_yuv import *



def calc_frqm(dist_path, ref_path):
    if '540' in ref_path:
        width = 960
        height = 540
    else:
        width = 1920
        height = 1080

    # # convert to yuv first
    # os.system('ffmpeg -hide_banner -loglevel error -i {} frqm_ref.yuv'.format(ref_path))
    # os.system('ffmpeg -hide_banner -loglevel error -i {} frqm_dist.yuv'.format(dist_path))

    cap_dist = cv2.VideoCapture(dist_path)
    cap_ref = cv2.VideoCapture(ref_path)
    
    dist_fps = int(cap_dist.get(cv2.CAP_PROP_FPS))
    ref_fps = int(cap_ref.get(cv2.CAP_PROP_FPS))
    # print(f'dist_fps {dist_fps}, ref_fps {ref_fps}')

    # assert int(cap_dist.get(cv2.CAP_PROP_FRAME_COUNT)) == int(cap_ref.get(cv2.CAP_PROP_FRAME_COUNT))

    num_frames_dist = int(cap_dist.get(cv2.CAP_PROP_FRAME_COUNT))
    num_frames_ref = int(cap_ref.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f'num_frames_dist {num_frames_dist}')
    print(f'num_frames_ref {num_frames_ref}')
    cap_dist.release()
    cap_ref.release()


    stream_dist = open('frqm_dist.yuv', 'rb') # frqm_dist.yuv data/test_15fps.yuv
    stream_ref = open('frqm_ref.yuv', 'rb') # frqm_ref.yuv data/test_60fps.yuv
    frames_hfr, frames_lfr = [], [] # high, low, i.e. ref dist

    # print(f'width, height {width, height}')
    file_size = os.path.getsize('frqm_ref.yuv')
    print(f'file_size ref {file_size}')


    for iFrame in range(num_frames_dist):
        frame_dist_y, _, _ = read_frame_yuv(stream_dist, width, height, iFrame, 8, pix_fmt='420')
        frames_lfr.append(frame_dist_y)
    
    for iFrame in range(num_frames_ref):
        frame_ref_y, _, _ = read_frame_yuv(stream_ref, width, height, iFrame, 8, pix_fmt='420')
        frames_hfr.append(frame_ref_y)
        
    stream_dist.close()
    stream_ref.close()

    ds = ref_fps // dist_fps
    print(f'\nds {ds}, dist_fps {dist_fps}, ref_fps {ref_fps} ')
    print(f'frames_lfr {np.array(frames_lfr).shape}') # frames_lfr -- shape (num_frames,H,W)
    frames_lfr_up = temporal_upsample(np.array(frames_lfr), dist_fps, ref_fps, num_frames_ref)
    print(f'frames_lfr_up {frames_lfr_up.shape}')
    print(f'frames_hfr {np.array(frames_lfr_up).shape}')


    # # delete files, modify command accordingly
    # os.remove('frqm_dist.yuv')
    # os.remove('frqm_ref.yuv')

    # fps = int(ref_path.split('_')[-2].split('f')[0])
    frqm = compute_frqm(np.array(frames_hfr), np.array(frames_lfr_up), fps_h=ref_fps)

    print(f'frqm {frqm}')

    return frqm



dist_path = 'refOutput_30_1080_8000.mp4'
ref_path = 'refOutput.mp4'

calc_frqm(dist_path, ref_path)





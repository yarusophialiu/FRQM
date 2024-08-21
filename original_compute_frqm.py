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

    # convert to yuv first
    os.system('ffmpeg -hide_banner -loglevel error -i {} frqm_ref.yuv'.format(ref_path))
    os.system('ffmpeg -hide_banner -loglevel error -i {} frqm_dist.yuv'.format(dist_path))

    cap_dist = cv2.VideoCapture(dist_path)
    cap_ref = cv2.VideoCapture(ref_path)
    assert int(cap_dist.get(cv2.CAP_PROP_FRAME_COUNT)) == int(cap_ref.get(cv2.CAP_PROP_FRAME_COUNT))
    num_frames = int(cap_ref.get(cv2.CAP_PROP_FRAME_COUNT))
    cap_dist.release()
    cap_ref.release()
    stream_dist = open('frqm_dist.yuv', 'r')
    stream_ref = open('frqm_ref.yuv', 'r')

    frames_hfr, frames_lfr_up = [], []
    for iFrame in range(num_frames):
        frame_ref_y, _, _ = read_frame_yuv(stream_ref, width, height, iFrame, 8, pix_fmt='420')
        frame_dist_y, _, _ = read_frame_yuv(stream_dist, width, height, iFrame, 8, pix_fmt='420')
 
        frames_lfr_up.append(frame_dist_y)
        frames_hfr.append(frame_ref_y)

    stream_dist.close()
    stream_ref.close()

        # delete files, modify command accordingly

    os.remove('frqm_dist.yuv')
    os.remove('frqm_ref.yuv')

 

    fps = int(ref_path.split('_')[-2].split('f')[0])
    frqm = compute_frqm(np.array(frames_hfr), np.array(frames_lfr_up), fps_h=fps)

 

    return frqm
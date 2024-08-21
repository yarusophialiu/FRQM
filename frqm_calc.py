import os
import math
import numpy as np
import torch
import torch.nn.functional as F
import cv2
import pywt


def read_images(root_path, seq_name, fps_h, fps_l, start_idx, end_idx):
    """
    returns two np arrays both of shape (1, 1, num_frames, H, W) 

    args:
    root_path -- str, directory of the dataset folder
    seq_name -- str, name of the sequence
    fps_h -- int, high fps
    fps_l -- int, low fps
    start_idx -- int, index of the starting frame
    end_idx -- int, index of the ending frame + 1
    """

    video_hfr, video_lfr = [], []

    # downsample ratio
    ds = int(fps_h / fps_l)

    # make sure #frames in hfr is ds times #frames in lfr
    if (end_idx - start_idx) % ds != 0:
        end_idx -= ((end_idx - start_idx) % ds)

    # read 120Hz images
    frames_path = os.path.join(root_path, str(fps_h)+'Hz', seq_name, 'frames')
    for idx in range(start_idx, end_idx):
        im_bgr = cv2.imread(os.path.join(frames_path, str(idx)+'.png'))
        im_Y = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2YCR_CB)[:,:,0] # HxW
        video_hfr.append(im_Y[:,:]) 
    
    # read 60Hz images
    frames_path = os.path.join(root_path, str(fps_l)+'Hz', seq_name, 'frames')
    for idx in range((start_idx+ds-1)//ds, (end_idx+ds-1)//ds):
        im_bgr = cv2.imread(os.path.join(frames_path, str(idx)+'.png'))
        im_Y = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2YCR_CB)[:,:,0] # HxW
        video_lfr.append(im_Y[:,:]) 

    return np.array(video_hfr), np.array(video_lfr)


def temporal_upsample(frames_lfr, test_fps, ref_fps, reference_vidr_frames):
    """
    Returns temporally nearest-neighbour upsampled version of the LFR test video,
    with number of frames equal to the reference HFR video.

    args:
    frames_lfr -- np array, of shape (num_frames,H,W)
    ds -- int, downsample ratio
    """

    num_frames, H, W = frames_lfr.shape

    # ====================== from cvvdp ======================
    max_fps = 166
    if test_fps % 1 == 0 and ref_fps % 1 == 0:
        gcd = math.gcd(int(test_fps),int(ref_fps))
        number1 = test_fps * ref_fps/gcd
        # print(f'number1 {number1}')
        resample_fps = min( test_fps * ref_fps/gcd, max_fps )
    else:
        resample_fps = max_fps

    frames_resampled = min( int(num_frames * resample_fps/test_fps ), int( reference_vidr_frames * resample_fps/ref_fps ) )
    print(f'frames_resampled {frames_resampled}')
    # return F.interpolate(torch.Tensor(frames_lfr[None,None,...]), size=(ds*num_frames, H, W), mode='nearest').numpy()[0,0]
    return F.interpolate(torch.Tensor(frames_lfr[None,None,...]), size=(frames_resampled, H, W), mode='nearest').numpy()[0,0]



def temporal_DWT(frames, filter, N):
    """
    Perform DWT along time axis. Return upsampled band coeffs of shape (N,num_frames,H,W)

    args:
    frames -- np.array of shape (num_frames,H,W)
    filter -- str, wavelet name
    N -- int, levels to decompose
    """

    # first flatten the images (num_frames, H, W) -> (HxW, num_frames)
    num_frames, H, W = frames.shape
    frames = frames.reshape((num_frames, H*W)).T # (HxW, num_frames)

    # perform 1D DWT along time axis at N levels and get HF coeffs (lo to hi, N to 1)
    HF_coeffs = pywt.wavedec(frames, 'haar', mode='symmetric', level=N, axis=1)[1:]

    # reshape and upsample each band coeff
    B = []
    for HF_band in HF_coeffs:
        HF_band = HF_band.T.reshape((HF_band.shape[1], H, W)) # (t',H,W)
        HF_band = F.interpolate(torch.Tensor(HF_band[None,None,...]), size=(num_frames, H, W), mode='nearest').numpy()[0,0] # (num_frames,H,W)
        B.append(HF_band)

    return np.array(B)



def pool_spatiotemporal(Dc, s, l):
    """
    Perform spatio-temporal pooling of the subband difference tensor.

    args:
    Dc -- np.array of shape (num_frames,H,W)
    s -- size of spatial window
    l -- length of temporal window
    """

    num_frames, H, W = Dc.shape

    if l > num_frames:
        l = 1

    # spatial pooling: take avg of 16x16 blocks, then take the max
    avg_filter = torch.ones(num_frames,1,s,s) / (s*s) # (num_frames,1,h,w)
    Dc_avg = F.conv2d(torch.Tensor(Dc[None,...]), avg_filter, stride=(s,s), groups=num_frames).numpy()[0] # (num_frames,h',w')
    Q_t = np.amax(Dc_avg, axis=(1,2)) # (num_frames,)

    # temporal pooling: take sum over temporal window, then take max over all sums
    sum_filter = torch.ones(1,1,l) / l # (1,1,l)
    Q = F.conv1d(torch.Tensor(Q_t[None,None,...]), sum_filter, stride=l).numpy()[0,0] # (num_frames/l, )
    Q = np.amax(Q)

    # convert to decibel units
    FRQM = 20 * np.log10(255/Q)

    return FRQM



def compute_frqm(frames_hfr, frames_lfr_up, fps_h, fps_l=None):
    fps_l = fps_h // 2
    # DWT
    N = int(np.ceil(np.log2(fps_h / fps_l)))
    B_ref = temporal_DWT(frames_hfr, filter='haar', N=N) # (N,num_frames,H,W)
    B_test = temporal_DWT(frames_lfr_up, filter='haar', N=N) # (N,num_frames,H,W)

    # obtain HF subband difference
    D = np.abs(B_ref - B_test)

    # multiply each subband with corresponding weight from the paper
    for n in range(N, 0, -1):
        freq = fps_h / (2**n)
        weight = 0.01 if freq == 60 else 0.03 if freq == 30 else 0.14
        D[N-n] = D[N-n] * weight 
    
    # sum the weighted coeffs along subband axis
    Dc = np.sum(D, axis=0) # (num_frames,H,W)
    
    # spatio-temporal pooling
    FRQM = pool_spatiotemporal(Dc, s=16, l=int(fps_h/5))

    return FRQM
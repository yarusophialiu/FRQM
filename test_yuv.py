from read_yuv import *
import os



# stream_ref = 'refOutput_30_360_8000.mp4'
width = 1080 # 1080 360
height = 1920 # 1920 640
frame_num = 2
yuv_filename = 'data/test_60fps.yuv' # 'frqm_ref.yuv'

file_size = os.path.getsize(yuv_filename)
print(f'file_size {file_size}')

# Number of frames: in YUV420 frame size in bytes is width*height*1.5
n_frames = file_size // (width*height*3 // 2)
print(f'n_frames {n_frames}')


stream_ref = open(yuv_filename, 'rb')



frame_ref_y, _, _ = read_frame_yuv(stream_ref, width, height, frame_num, bit_depth=8, pix_fmt='420')
print(f'frame_ref_y {frame_ref_y.shape} \n {frame_ref_y}\n\n')





frame_ref_y_me, _, _ = read_frame_yuv_me(stream_ref, width, height, frame_num, bit_depth=8, pix_fmt='420')
print(f'frame_ref_y_me {frame_ref_y_me.shape} \n {frame_ref_y_me}\n')

# # Load the reference frame extracted by FFmpeg and compare
# y_size = width * height
# with open('16.yuv', 'rb') as file:
#     ref_y = np.frombuffer(file.read(y_size), dtype=np.uint8).reshape((height, width))

# print(f'ref_y {ref_y.shape} \n {ref_y}')  # This should output (360, 640)
assert np.array_equal(frame_ref_y, frame_ref_y_me), "The frames do not match!"

# # ffmpeg -s 640x320 -i frqm_ref.yuv -frames:v 1 -vf "select=eq(n\,16)" 16.yuv

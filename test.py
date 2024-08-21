import math

ref_fps, target_fps = 166, 166
test_fps, original_fps = 30, 30
reference_vidr_frames = 277
test_vidr_frames = 51

ds = target_fps / original_fps
max_fps = 166
# First check if we can find an integer resampling rate
if test_fps % 1 == 0 and ref_fps % 1 == 0:
    gcd = math.gcd(int(test_fps),int(ref_fps))
    number1 = test_fps * ref_fps/gcd
    print(f'number1 {number1}')
    resample_fps = min( test_fps * ref_fps/gcd, max_fps )
else:
    resample_fps = max_fps

frames_resampled = min( int(test_vidr_frames * resample_fps/test_fps ), int( reference_vidr_frames * resample_fps/ref_fps ) )
frames = frames_resampled 

print( f"Resampling videos to {resample_fps} frames per second. {frames} frames will be processed." )
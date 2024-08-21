import numpy as np
# read_frame_yuv implemented by the author
# read_frame_yuv_me implemented by me
# both work, and produce the same result in test_yuv.py

def read_frame_yuv(stream, width, height, iFrame, bit_depth, pix_fmt='420'):
    if pix_fmt == '420':
        multiplier = 1
        uv_factor = 2
    elif pix_fmt == '444':
        multiplier = 2
        uv_factor = 1
    else:
        print('Pixel format {} is not supported'.format(pix_fmt))
        return

    if bit_depth == 8:
        datatype = np.uint8
        seek_num = int(iFrame*1.5*width*height*multiplier)
        # seek_num = int(iFrame*width*height*multiplier)
        # print(f'seek_num {seek_num}')
        stream.seek(seek_num)
        Y = np.fromfile(stream, dtype=datatype, count=width*height).reshape((height, width))
        # print(f'shape {Y.shape}')
        
        # read chroma samples and upsample since original is 4:2:0 sampling
        # U = np.fromfile(stream, dtype=datatype, count=(width//uv_factor)*(height//uv_factor)).\
        #                         reshape((height//uv_factor, width//uv_factor))
        # V = np.fromfile(stream, dtype=datatype, count=(width//uv_factor)*(height//uv_factor)).\
        #                         reshape((height//uv_factor, width//uv_factor))

    else:
        datatype = np.uint16
        stream.seek(iFrame*3*width*height*multiplier)
        Y = np.fromfile(stream, dtype=datatype, count=width*height).reshape((height, width))
                
        U = np.fromfile(stream, dtype=datatype, count=(width//uv_factor)*(height//uv_factor)).\
                                reshape((height//uv_factor, width//uv_factor))
        V = np.fromfile(stream, dtype=datatype, count=(width//uv_factor)*(height//uv_factor)).\
                                reshape((height//uv_factor, width//uv_factor))

    if bit_depth != 8:
        Y = (Y/(2**bit_depth-1)*255).astype(np.uint8)
        U = (U/(2**bit_depth-1)*255).astype(np.uint8)
        V = (V/(2**bit_depth-1)*255).astype(np.uint8)
    # return Y.astype(np.int32), U.astype(np.int32), V.astype(np.int32)
    return Y.astype(np.int32), None, None


def read_frame_yuv_me(file, width, height, frame_num, bit_depth, pix_fmt='420'):
    """
    frame_num: starts from 0
    pix_fmt: The pixel format, assumed to be '420' (YUV 4:2:0) in this implementation.
    bit_depth: The bit depth of the video (typically 8 bits for YUV 4:2:0).
    """
    # Calculate the size of the Y, U, and V components based on the format
    if pix_fmt == '420':
        frame_size = width * height * 3 // 2  # YUV 4:2:0 format
        print(f'frame_size {frame_size}')
        y_size = width * height
        uv_size = width * height // 4
    else:
        raise ValueError("Unsupported pixel format!")

    # Calculate the byte position of the frame
    frame_start = frame_num * frame_size

    # Seek to the correct position in the file
    file.seek(frame_start, 0)

     # Read the Y component
    if bit_depth == 8:
        y = np.frombuffer(file.read(y_size), dtype=np.uint8).reshape((height, width))
        # y = np.frombuffer(file.read(width*height*3//2), dtype=np.uint8).reshape((height*3//2, width))
    elif bit_depth == 10:
        y = np.frombuffer(file.read(y_size * 2), dtype=np.uint16).reshape((height, width)) >> 6
    elif bit_depth == 12:
        y = np.frombuffer(file.read(y_size * 2), dtype=np.uint16).reshape((height, width)) >> 4
    else:
        raise ValueError("Unsupported bit depth!")

    # # Read the U and V components, but in this case, we'll ignore them
    # u = np.frombuffer(file.read(uv_size), dtype=np.uint8).reshape((height // 2, width // 2))
    # v = np.frombuffer(file.read(uv_size), dtype=np.uint8).reshape((height // 2, width // 2))

    # Return the Y component and placeholders for U and V
    # return y, u, v
    return y, None, None

%   TEST_FRQM(): test function for main_FRQM()
%
%               TEST_FRQM calls main_FRQM() and generates quality indices
%   Output: 
%               FRQM_SQ -  sequence level index - FRQM (dB unit);
%
%   Disclaimer:
%
%       It is provided for educational/research purpose only.
%       If you find the software useful, please consider cite our paper.
%
%       "A Frame Rate Dependent Video Quality Metric based on Temporal Wavelet Decomposition and Spatiotemporal Pooling"
%       Fan Zhang, Alex Mackin and David Bull
%       IEEE ICIP, 2017
%
%   Contact:
%       Fan.Zhang@bristol.ac.uk, http://seis.bris.ac.uk/~eexfz/
%       Dave.Bull@bristol.ac.uk, http://www.bristol.ac.uk/engineering/people/david-r-bull/index.html
%       University of Bristol
%
%   Copyright 2018 VI-Lab, University of Bristol.
%   Date: August 2018

function test_FRQM()
fprintf('This is a sentence printed in MATLAB.\n')

params = struct(...
    'origYUV','.\data\test_60fps.yuv',...original sequence (high frame rate <=120fps, YUV420 format)
    'testYUV','.\data\test_30fps.yuv',...test sequence (low frame rate>=15fps, YUV420 format)
    'width',1920,... frame width
    'height', 1080,... frame height
    'bitDepth',8,...pixel bit depth
    'origFrameRate',60,...frame rate of the original sequence
    'testFrameRate',15,...frame rate of the test sequence
    'noOfFrames',(8)...the number of frames from the original sequences are tested
    );
fprintf('This is a sentence printed in MATLAB.\n')

[FRQM_SQ] = main_FRQM(params);











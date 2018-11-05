% obj = VideoReader("/Users/wzy/Desktop/IMG_1027.mov")
clc;
clear;
%% this to read avi by using mmread to get every frame
video = VideoReader('/Users/wzy/Desktop/light.mp4');
% video = VideoReader('/Users/wzy/Nutstore Files/大四上/跑冒滴漏-毕业设计/samples/water.mp4');
nFrames = video.NumberOfFrames;   %得到帧数
H = video.Height;     %得到高度
W = video.Width;      %得到宽度
Rate = video.FrameRate;
% Preallocate movie structure.
mov(1:nFrames) = struct('cdata',zeros(H,W,3,'uint8'),'colormap',[]);
 
disp(1)
%read one frame every time
outFile = zeros(240*135,nFrames);
for i = 1:nFrames
    mov(i).cdata = read(video,i);
    P = mov(i).cdata;
    P2=rgb2gray(P);
    J=imresize(P2, [135,240],'nearest');
%     disp('当前播帧数：'),disp(i);
%     imshow(J),title('原始图片');
    outFile(:,i)=J(:);
end
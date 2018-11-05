% obj = VideoReader("/Users/wzy/Desktop/IMG_1027.mov")
clc;
clear;
%% this to read avi by using mmread to get every frame
video = VideoReader('/Users/wzy/Desktop/light.mp4');
% video = VideoReader('/Users/wzy/Nutstore Files/������/��ð��©-��ҵ���/samples/water.mp4');
nFrames = video.NumberOfFrames;   %�õ�֡��
H = video.Height;     %�õ��߶�
W = video.Width;      %�õ����
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
%     disp('��ǰ��֡����'),disp(i);
%     imshow(J),title('ԭʼͼƬ');
    outFile(:,i)=J(:);
end
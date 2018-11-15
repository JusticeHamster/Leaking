import numpy as np
import cv2
import lktools

settings = lktools.Loader.get_settings()
img_path = settings['img_path']
def run(name, video):
    cap = cv2.VideoCapture(video)

    # ShiTomasi 角点检测参数
    feature_params = dict( maxCorners = 200,
                        qualityLevel = 0.01,
                        minDistance = 8,
                        blockSize = 3 )

    # lucas kanade光流法参数
    lk_params = dict( winSize  = (22,22),
                    maxLevel = 5,
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.CV_TERMCRIT_ITER, 20, 0.01))

    # 创建随机颜色
    color = np.random.randint(0,255,(100,3))

    # 获取第一帧，找到角点
    _, old_frame = cap.read()
    # 找到原始灰度图
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

    # 获取图像中的角点，返回到p0中
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

    # 创建一个蒙版用来画轨迹
    mask = np.zeros_like(old_frame)

    count = 0
    while True:
        success, frame = cap.read()
        count += 1
        if count % 5 == 0:
            continue
        if not success:
            break
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 计算光流
        p1, st, _ = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
        # 选取好的跟踪点
        good_new = p1[st==1]
        good_old = p0[st==1]

        # 画出轨迹
        for i,(new,old) in enumerate(zip(good_new,good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
            frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
        img = cv2.add(frame,mask)

        cv2.imwrite(
            '{path}/{name}_{i}.jpg'.format(
                path=img_path,
                name=name,
                i=count
            ),
            cv2.resize(img, (520, 960))
        )

        # 更新上一帧的图像和追踪点
        old_gray = frame_gray
        p0 = good_new.reshape(-1,1,2)

    cv2.destroyAllWindows()
    cap.release()
# run
if __name__ == '__main__':
    for name, video in settings['videos']:
        run(name, video)
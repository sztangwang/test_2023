__author__ = 'UniDome'
__version__ = '1.0.1'

import cv2
import os, sys
from pathlib import Path
import glob
from tqdm import tqdm
import numpy as np

FILE = Path(__file__).resolve() # 当前文件所在绝对路径
ROOT = FILE.parents[0]

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # 当前文件所在相对路径

IMG_FORMATS = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']
VID_FORMATS = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']
VID_MKFORMATS = ['avi', 'mp4']
VID = ['.' + x for x in VID_FORMATS]

class Frame(object):
       
    def __init__(
        self, 
        video_path:ROOT, 
        step:int=None, 
        fps:int=60, 
        start:int=None, 
        end:int=None, 
        use_file_name:bool=False,
        img_format:str='jpg'
        ) -> None:
        
        self.step = step if step is not None else 1
        self.fps = fps 
        self.start = start
        self.end = end
        self.use_file_name = use_file_name
        self.img_format = img_format
        
        p = str(Path(video_path).resolve())
        if os.path.isdir(p):
            dir_file = os.listdir(video_path)
            files_v = [pa for pa in dir_file if os.path.splitext(pa)[-1] in VID]
            files = [os.path.join(p, file) for file in files_v]
        elif os.path.isfile(p):
            assert os.path.splitext(p)[-1] in [ x for x in VID], f'Supported formats are:\nimages: {VID_FORMATS}'
            files = [p]
        else:
            raise Exception(f'ERROR: {p} does not exist')

        self.nv = len(files)
        self.count = 0
        self.videos = files
        self.pps = 0	# 当前帧所处位号
        self.frame = 0

        assert self.nv > 0, f'No images or videos found in {p}. ' \
                            f'Supported formats are:\nvideos: {VID_FORMATS}'
        assert self.img_format in IMG_FORMATS, f'Supported formats are:\nimages: {IMG_FORMATS}'
        assert self.step > 0, f'FPS {self.step} is illegal'
        assert self.fps > 0, f'FPS {self.fps} is illegal'

        print(f'INFORMATION\ntotal find {self.nv} files:\n{self.videos}') 

        self.new_video(self.videos[0])

        if self.start is not None:
            self.start = self.time_str_to_sec(self.start) * self.fps
        else:
            self.start = 0

        if self.end is not None:
            self.end = self.time_str_to_sec(self.end) * self.fps
        else:
            self.end = self.frames

        if self.use_file_name:
            self.file_name = Path(self.videos[0]).stem + '_'
        else:
            self.file_name = ''

        print(f'make images\t{self.start} --> {self.end}')     

    def __iter__(self):
        return self

    def __next__(self):
        if self.count == self.nv:
            raise StopIteration
        path = self.videos[self.count]
        ret, img = self.cap.read()
        if not ret:
            self.check_and_get_new()
            ret, img = self.cap.read()

        if self.frames < self.end:
            print('Video duration is too short')
            self.check_and_get_new()
            ret, img = self.cap.read()
        
        while self.pps < self.start:
            print(f'Loading Video File {path}', end='\r')
            self.pps += 1
            ret, img = self.cap.read()
            if not ret:
                self.check_and_get_new()
                ret, img = self.cap.read()
        if self.pps == self.start:
            print('\nLoad Complete\nSaving Images\nPlease Waiting···')

        while self.pps % self.step != 0:
            self.pps += 1
            ret, img = self.cap.read()
            if not ret:
                self.check_and_get_new()
                ret, img = self.cap.read()

        if self.pps >= self.start and self.pps < self.end:
            self.frame += 1
            self.pps += 1
            img_name = '{:0>8d}.{}'.format(self.frame - 1, self.img_format)
            img_name = self.file_name + img_name
            #print(f'video {self.count + 1}/{self.nv} ({self.frame}/{(self.end - self.start)/self.fps}) {img_name}: ', end='')
            return path, img, self.frame, img_name
        else:
            return self.check_next()

   

    def check_and_get_new(self):
    	# 检查是否已经读取完成，如果队列中还有视频，则开始读取新的视频
        self.count += 1
        self.cap.release()
        if self.count == self.nv:
            raise StopIteration
        else:
            path = self.videos[self.count]
            if self.use_file_name:
                self.file_name = Path(path).stem + '_'
            self.new_video(path)

    def time_str_to_sec(self, time):
    	# 转换时间格式
        time = time.replace('：',':')
        time_list = time.split(':')
        if len(time_list) == 1:
            return int(time_list[0])
        elif len(time_list) == 2:
            return int(time_list[0]) * 60 + int(time_list[1])
        elif len(time_list) == 3:
            return int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])

    def new_video(self, path):
    	# 读取一个视频文件
        self.frame = 0
        self.cap = cv2.VideoCapture(path)
        self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.pps = 0
        print(f'\nOpen Video {path}')

    def __len__(self):
        return self.nv

class Video():

    def __init__(
        self, 
        images:ROOT,
        video_name:str=None, 
        video_format:str='mp4',
        image_format:str='jpg',
        size:list=None,
        fps:int=60,
        output:str='./output'
        ):

        '''
            images: 图片所在目录  
            video_name: 保存的视频名
            video_format: 保存的视频格式 
            image_format: 选取的图片格式
            size: 合并图片的resize大小
            fps: 合成视频的帧率
            output: 视频输出目录      
        '''

        print('Checking···\nINFORMATION')
        images = Path(images)
        size = size if size is not None else ['auto']

        assert os.path.isdir(images), 'Images path is invalid'
        # assert video_name is not None, 'Video name is None'
        assert video_format in VID_FORMATS, f'Supported video formats are:\nimages: {VID_MKFORMATS}'
        assert image_format in IMG_FORMATS, f'Supported images formats are:\nimages: {IMG_FORMATS}'

        if video_name is None:
            video_name=os.path.split(Path(images).resolve())[-1]

        imgs = os.listdir(images)
        imgs = [img for img in imgs if os.path.splitext(img)[-1]==('.' + image_format)]
        imgs.sort()
        self.imgs = [os.path.join(Path(images), img) for img in imgs]

        self.size = size
        self.fps = fps
        self.output = output

        fourcc = {'mp4':'mp4v', 'avi':'DIVX'}
        self.fourcc = fourcc[video_format]

        if os.path.splitext(video_name)[-1] == ('.' + video_format):
            self.video = os.path.join(Path(output), video_name)
        else:
            video_name += '.' + video_format
            self.video = os.path.join(Path(output), video_name)

        print(f'Images from {images}\tVideo name: {video_name}\nImage Format: {image_format}\tVideo Format: {video_format}\nImage Size: {size}\tFPS: {fps}')
        print(f'Video will Save to {self.video}')


def calculate(image1, image2):
    # 灰度直方图算法
    # 计算单通道的直方图的相似值
    hist1 = cv2.calcHist([image1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0.0, 255.0])
    # 计算直方图的重合度
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + \
                (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree
 

def classify_hist_with_split(image1, image2, size=(256, 256)):
    # RGB每个通道的直方图相似度
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data[0]


def video_to_image(
    video_path:ROOT, 
    step:int=None, 
    fps:int=60, 
    start:int=None, 
    end:int=None, 
    use_file_name:bool=False,
    img_format:str='jpg',
    save_path:ROOT='./images'
    ):
    # 视频拆帧函数
    '''
        video_path: ROOT -> 视频路径（或视频所在文件目录）
        step: int -> 间隔帧率，默认不间隔取帧
        fps: int -> 视频帧率，默认25帧
        start: str -> 开始时间（00:00:00），默认视频开始时间
        end: str -> 结束时间（00:00:00），默认视频结束时间
        use_file_name: bool -> 是否使用视频文件名作为命名规范
        img_format: str -> 保存的图片格式
        save_path: ROOT -> 保存的文件路径
    '''
    
	# 实例化迭代器
    video  = Frame(video_path, step=step, fps=fps,start=start,end=end, use_file_name=use_file_name,img_format=img_format)
    i = 0
    j = 0
    for path, img, frame, name in video:
        dir_path = os.path.join(Path(save_path), Path(path).stem)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        save_img_path = os.path.join(dir_path, name)
        cv2.imwrite(save_img_path, img)

        if i == 1:

            img1 = cv2.imread(img_path)
            img2 = cv2.imread(save_img_path)
            # img1 = img1[300:1700, 700:1200]
            # img2 = img2[300:1700, 700:1200]
           
            gray_base = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray_cur = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            resImg = cv2.absdiff(gray_cur, gray_base)

            # threshold阈值函数(原图像应该是灰度图,对像素值进行分类的阈值,当像素值高于（有时是小于）阈值时应该被赋予的新的像素值,阈值方法)
            thresh = cv2.threshold(resImg, 30, 255, cv2.THRESH_BINARY)[1]
            # 用一下腐蚀与膨胀
            thresh = cv2.dilate(thresh, None, iterations=2)
            # findContours检测物体轮廓(寻找轮廓的图像,轮廓的检索模式,轮廓的近似办法)
            contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            num = 0 
            # print(img_path)
            # print(save_img_path)
            # print('############################')
            for c in contours:
                # 设置敏感度
                # contourArea计算轮廓面积
                if cv2.contourArea(c) > 800:
                    num = num + 1
                    
               
            #print(num)       
            if num < 2:
                print('#####',cv2.contourArea(c))
                
              
                print(img_path)
                print(save_img_path)


        i = 1
        img_path = save_img_path
    print('\nSave Done')





if __name__ == '__main__':
    video_path = 'D://1.mkv'
    video_to_image(video_path, step=1)	# 视频拆帧
    
 
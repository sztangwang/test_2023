# -*-coding:UTF-8-*- #
"""
Author: LinZF
Package: 
"""
import cv2
import time
import numpy
import imutils
import math
import pyautogui
import numpy as np
from PIL import Image
from ui.test.record.Util import TFile




# 图像效果枚举值
BLACK = "Black"
WHITE = "White"
GREY = "Grey"
BLUE = "Blue"
GREEN = "Green"
RED = "Red"
OTHER_SOLID_COLOR = "Other solid color"
NORMAL = "Normal"
MOSAIC = "Mosaic"
GREY_SCALE = "Grey scale"
OTHER = "Other"
PURITY = "purity"

# 数据类型枚举值
DEFAULT = "numpy.uint8"
NUMPY_INT = "numpy.int_"

SCREEN_MODE_4_3 = "4:3"
SCREEN_MODE_5_3 = "5:3"
SCREEN_MODE_16_9 = "16:9"

FLAG_16 = True
wrong_d_value_index_list = []

def opencv_image_complete(out_time=10):
    #times图像录制时间
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    is_one_image = True # 用于是否是第一张图片
    
    picture_path = TFile.get_complete_picture_path()
    while int(time.time() - start_time) < out_time:
        ret, frame = cap.read()
        image_path = "%s\%s.jpg"%(picture_path,TFile.get_datetime())
        if is_one_image:
            one_image = image_path
            is_one_image = False

        cv2.imwrite(image_path, frame)
        if not is_one_image:
           
            if not get_image_similarity(image_path,one_image):
                print(image_path)
                print(one_image)
                return
    cap.release()


def get_image_rgb(path, area=None, d_type=DEFAULT):
    # img = cv2.imread(path)
    img = cv2.imdecode(numpy.fromfile(path, dtype=numpy.uint8), 1)
    if (isinstance(area, list) or isinstance(area, tuple)) and len(area) == 4:
        img = img[area[1]:area[3], area[0]:area[2]]
    (b, g, r) = cv2.split(img)
    if d_type == NUMPY_INT:
        return r.astype(numpy.int_), g.astype(numpy.int_), b.astype(numpy.int_)
    else:
        return r, g, b


# 出现次数最多的r,g,b
def get_argmax_rgb(path, area=None):
    r, g, b = get_image_rgb(path, area)
    red = []
    green = []
    blue = []
    for line in r:
        red.extend(line)
    for line in g:
        green.extend(line)
    for line in b:
        blue.extend(line)
    return numpy.argmax(numpy.bincount(red)), numpy.argmax(numpy.bincount(green)), numpy.argmax(numpy.bincount(blue))


def get_min_rgb(path, area=None):
    r, g, b = get_image_rgb(path, area, NUMPY_INT)
    return numpy.min(r), numpy.min(g), numpy.min(b)


def get_max_rgb(path, area=None):
    r, g, b = get_image_rgb(path, area, NUMPY_INT)
    return numpy.max(r), numpy.max(g), numpy.max(b)


def get_mean_rgb(path, area=None):
    r, g, b = get_image_rgb(path, area, NUMPY_INT)
    return numpy.mean(r), numpy.mean(g), numpy.mean(b)


def get_rgb_min_d_value(path):
    r, g, b = get_image_rgb(path, d_type=NUMPY_INT)
    return numpy.min(abs(r-g)), numpy.min(abs(g-b)), numpy.min(abs(b-r))


def get_rgb_max_d_value(path):
    r, g, b = get_image_rgb(path, d_type=NUMPY_INT)
    return numpy.max(abs(r-g)), numpy.max(abs(g-b)), numpy.max(abs(b-r))


def get_rgb_mean_d_value(path):
    r, g, b = get_image_rgb(path, d_type=NUMPY_INT)
    return numpy.mean(abs(r - g)), numpy.mean(abs(g - b)), numpy.mean(abs(b - r))


def get_rgb_std_d_value(path):
    r, g, b = get_image_rgb(path, d_type=NUMPY_INT)
    return numpy.std(r - g), numpy.std(g - b), numpy.std(b - r)


# 获取图片的哈希值
def get_hash(path, width=64, area=None):
    # 读取图片
    # src = cv2.imread(path, 0)
    src = cv2.imdecode(numpy.fromfile(path, dtype=numpy.uint8), 0)
    # 取出图片的部分区域
    if isinstance(area, list) and len(area) == 4:
        src = src[area[1]:area[3], area[0]:area[2]]
    # 将图片压缩为64*64，并转化为灰度图
    gray_img = cv2.resize(src, (width, width), cv2.COLOR_BGR2GRAY, interpolation=cv2.INTER_LANCZOS4)
    # 计算图片的平均灰度值
    avg = numpy.mean(gray_img)
    # 计算哈希值
    hash_str = ""
    for index in range(width):
        hash_str += ''.join(map(lambda i: '0' if i < avg else '1', gray_img[index]))
    # 计算哈希值，将4096位的哈希值，每4位转化为16进制数
    hex_hash = ""
    for index in range(0, width*width, 4):
        hex_hash += ''.join('%x' % int(hash_str[index: index+4], 2))
    return hex_hash


# 计算汉明距离
def get_graphics_hamming_distance(h1, h2):
    if len(h1) != len(h2):
        return 0, 0
    count = 0
    for index in range(len(h1)):
        if h1[index] != h2[index]:
            count += 1
    return count, len(h1)


def get_color(path1, path2, width=64, area=None):
    # 读取图片
    # src1 = cv2.imread(path1)
    src1 = cv2.imdecode(numpy.fromfile(path1, dtype=numpy.uint8), 1)
    # src2 = cv2.imread(path2)
    src2 = cv2.imdecode(numpy.fromfile(path2, dtype=numpy.uint8), 1)
    # 取出图片的部分区域
    if isinstance(area, list) and len(area) == 4:
        src1 = src1[area[1]:area[3], area[0]:area[2]]
        src2 = src2[area[1]:area[3], area[0]:area[2]]
    # 当两张图片大小不一致时，将图片压缩为64*64
    if src1.shape[0] != src2.shape[0] or src1.shape[1] != src2.shape[1]:
        src1 = cv2.resize(src1, (width, width), interpolation=cv2.INTER_LANCZOS4)
        src2 = cv2.resize(src2, (width, width), interpolation=cv2.INTER_LANCZOS4)
    # 将数值转换为int类型
    int_src1 = src1.astype(numpy.int_)
    int_src2 = src2.astype(numpy.int_)
    return int_src1, int_src2







def get_picture_status(image,is_cut=True):
    # img = cv2.imread(image)
    img = cv2.imdecode(numpy.fromfile(image, dtype=numpy.uint8), 1)
    if is_cut:
        img = img[200:1100, 0:1200]
    # cv2.imshow("aa",img)
    # cv2.waitKey(0)
    (b, g, r) = cv2.split(img)
    b_avg, b_min, b_max, b_std = numpy.mean(b), numpy.min(b), numpy.max(b), numpy.std(b)
    g_avg, g_min, g_max, g_std = numpy.mean(g), numpy.min(g), numpy.max(g), numpy.std(g)
    r_avg, r_min, r_max, r_std = numpy.mean(r), numpy.min(r), numpy.max(r), numpy.std(r)

    print(numpy.max([b_std, g_std, r_std]))
    print(numpy.std([b_avg, g_avg, r_avg]))
    if b_min >= 64 and r_avg < (255-3*r_avg)/255*b_avg and g_avg <= b_avg*b_avg/255:
        return BLUE
    elif g_min >= 64 and numpy.max([b_avg, r_avg]) < g_avg*(1 - g_avg/510) and numpy.max([b_avg, r_avg]) < g_avg-48:
        return GREEN
    elif r_min >= 64 and b_avg < r_avg/3 and g_avg < r_avg/4 and numpy.max([b_avg, r_avg]) < g_avg-48:
        return RED
    elif numpy.mean([b_avg, g_avg, r_avg]) < 64 and numpy.max([b_max, g_max, r_max]) < 80:
        return BLACK
    elif numpy.mean([b_avg, g_avg, r_avg]) > 215 and numpy.min([b_min, g_min, r_min]) > 199:
        return WHITE
    
    elif numpy.max([b_std, g_std, r_std]) < 8:
        return PURITY
    
    elif numpy.std([b_avg, g_avg, r_avg]) < 7 and numpy.max([b_std, g_std, r_std]) < 10:
        return GREY
    return OTHER_SOLID_COLOR
  


def get_brightness(path, area=None):
    # img = cv2.imread(path, 0)
    img = cv2.imdecode(numpy.fromfile(path, dtype=numpy.uint8), 0)
    if isinstance(area, list) and len(area) == 4:
        img = img[area[1]:area[3], area[0]:area[2]]
    return numpy.mean(img)


def get_screen_mode(path, width=1920, height=1080):
    left, top, right, bottom = 0, 0, width, height
    for w in range(1, width+1):
        if numpy.max(get_max_rgb(path, [0, 0, w, height])) > 24:
            break
        left = w
    for w in range(width-1, -1, -1):
        if numpy.max(get_max_rgb(path, [w, 0, width, height])) > 24:
            break
        right = w
    for h in range(1, height+1):
        if numpy.max(get_max_rgb(path, [0, 0, width, h])) > 24:
            break
        top = h
    for h in range(height-1, -1, -1):
        if numpy.max(get_max_rgb(path, [0, h, width, height])) > 24:
            break
        bottom = h
    TLog.debug("画面显示区域, Area=%s" % [left, top, right, height])
    if right <= left or bottom <= top or abs(left + right - width) > 5 or abs(top + bottom - height) > 5:
        return None
    elif abs((right - left)/16 - (bottom - top)/9) < 10/25:
        return SCREEN_MODE_16_9
    elif abs((right - left)/4 - (bottom - top)/3) < 10/7:
        return SCREEN_MODE_4_3
    elif abs((right - left)/5 - (bottom - top)/3) < 10/8:
        return SCREEN_MODE_5_3
    else:
        return None


# 获取指定坐标x,y处的RGB值,pointlist=[x,y]
def get_point_rgb(path, pointlist):
    img = Image.open(path)
    img = img.convert('RGB')
    RGBlist = img.load()
    datas = list(RGBlist[pointlist[0], pointlist[1]])
    img.close()
    return datas


# 获取指定坐标x,y处的RGB值三个数的平均值,pointlist=[x,y]
def get_point_rgb_mean(path, pointlist):
    img = Image.open(path)
    img = img.convert('RGB')
    RGBlist = img.load()
    datas = list(RGBlist[pointlist[0], pointlist[1]])
    img.close()
    mean_data = (datas[0] + datas[1] + datas[2]) / 3
    return mean_data


def classify_hist_with_split(image1, image2, size=(256, 256)):
    # RGB每个通道的直方图相似度
    # 将图像resize后，分离为RGB三个通道，再计算每个通道的相似值
    image1 = cv2.imread(image1)
    image2 = cv2.imread(image2)
    image1 = cv2.resize(image1, size)
    image2 = cv2.resize(image2, size)
    sub_image1 = cv2.split(image1)
    sub_image2 = cv2.split(image2)
    sub_data = 0
    for im1, im2 in zip(sub_image1, sub_image2):
        sub_data += calculate(im1, im2)
    sub_data = sub_data / 3
    return sub_data[0]

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
 
def get_pc_screen(x,y,x2=500,y2=500,keyword="base"):
    img = pyautogui.screenshot(region=[x,y, x2, y2])  # 分别代表：左上角坐标，宽高
    img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    file = TFile.get_cache_picture(keyword = keyword)
    cv2.imwrite(file,img)
    return file


def get_opencv_image_comparison(image1, image2):
    """ opencv 图像对比方法 """
    img1 = cv2.imread(image1)
    img2 = cv2.imread(image2)
    
    gray_base = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray_cur = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    resImg = cv2.absdiff(gray_cur, gray_base)

    # threshold阈值函数(原图像应该是灰度图,对像素值进行分类的阈值,当像素值高于（有时是小于）阈值时应该被赋予的新的像素值,阈值方法)
    thresh = cv2.threshold(resImg, 30, 255, cv2.THRESH_BINARY)[1]
    # 用一下腐蚀与膨胀
    thresh = cv2.dilate(thresh, None, iterations=2)
    # findContours检测物体轮廓(寻找轮廓的图像,轮廓的检索模式,轮廓的近似办法)
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = 0 
    for c in contours:
        # 设置敏感度
        # contourArea计算轮廓面积
        result = int (cv2.contourArea(c) / 600 + result)
       
    return result

def set_opencv_contourArea(image1,image2):
    """ opencv 绘制不同点 轮廓方块"""
    img1 = cv2.imread(image1)
    img2 = cv2.imread(image2)
    gray_base = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray_cur = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    resImg = cv2.absdiff(gray_cur, gray_base)
    # threshold阈值函数(原图像应该是灰度图,对像素值进行分类的阈值,当像素值高于（有时是小于）阈值时应该被赋予的新的像素值,阈值方法)
    thresh = cv2.threshold(resImg, 30, 255, cv2.THRESH_BINARY)[1]
    # 用一下腐蚀与膨胀
    thresh = cv2.dilate(thresh, None, iterations=2)
    # findContours检测物体轮廓(寻找轮廓的图像,轮廓的检索模式,轮廓的近似办法)
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(contours)
    for c in cnts:
        # 设置敏感度
        #contourArea计算轮廓面积
        (x, y, w, h) = cv2.boundingRect(c)
        if cv2.contourArea(c) > 500:  # 设置轮廓面积小于 500则绘画
            cv2.rectangle(img1, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return img1,img2


def get_redisplay_percent_x(img, fixed_y=None):
    """
    获取垂直方向上的重现率
    :param img: 传入的图片
    :param fixed_y: 固定的y坐标
    :return: x轴重现率的值
    """
    # image = cv2.imread(img)
    image = cv2.imdecode(numpy.fromfile(img, dtype=numpy.uint8), 1)
    shape = image.shape
    height = shape[1]
    width = shape[0]
    # y轴的坐标值得列表
    coordinates_x_left = []
    coordinates_x_right = []
    Y = int(width / 2 + 5)

    REDISPLAY_PERCENT_HORIZONTAL_LEFT_RANGE = TFile.load_config("RedisplayPercentHorizontalLeftRange")
    REDISPLAY_PERCENT_HORIZONTAL_RIGHT_RANGE = TFile.load_config("RedisplayPercentHorizontalRightRange")
    REDISPLAY_PERCENT_R_G_B = TFile.load_config("RedisplayPercentRGB")
    R = REDISPLAY_PERCENT_R_G_B[0]
    G = REDISPLAY_PERCENT_R_G_B[1]
    B = REDISPLAY_PERCENT_R_G_B[2]
    end = 0
    start = 0
    for i in range(int(height / 2), height):
        if image[int(width / 2), i, 0] < R and image[int(width / 2), i, 0] < G and image[int(width / 2), i, 0] < B:
            end = i
            start = int(height / 2) - (end - int(height / 2))
            break
    for i in range(REDISPLAY_PERCENT_HORIZONTAL_LEFT_RANGE[0], REDISPLAY_PERCENT_HORIZONTAL_LEFT_RANGE[1]):
        if image[Y, i, 0] > R and image[Y, i, 2] > G and image[Y, i, 2] > B:
            if not (image[Y, i + 1, 0] > R and image[Y, i + 1, 2] > G and image[Y, i + 1, 2] > B):
                coordinates_x_left.append(i)
    for i in range(REDISPLAY_PERCENT_HORIZONTAL_RIGHT_RANGE[0], REDISPLAY_PERCENT_HORIZONTAL_RIGHT_RANGE[1]):
        if image[Y, i, 0] > R and image[Y, i, 2] > G and image[Y, i, 2] > B:
            if not (image[Y, i - 1, 0] > R and image[Y, i - 1, 2] > G and image[Y, i - 1, 2] > B):
                coordinates_x_right.append(i)
    if (not coordinates_x_left) or (not coordinates_x_right):
        TLog.api_error("获取白色竖线失败检查配置")
        return None
    avg_distance_left = get_average_distance_redisplay(coordinates_x_left)
    avg_distance_right = get_average_distance_redisplay(coordinates_x_right)
    percent_left = round(90 + (coordinates_x_left[-1] / avg_distance_left), 2)
    percent_right = round(90 + ((height - coordinates_x_right[0]) / avg_distance_right), 2)
    if percent_left > 102:
        percent_left = round(90 + ((coordinates_x_left[-1] - start)/avg_distance_left), 2)
    if percent_right > 102:
        percent_right = round(90 + ((end - coordinates_x_right[0])/avg_distance_right), 2)
    result = min([percent_left, percent_right])
    if abs(int(result) - result) < abs(math.ceil(result) - result):
        return int(result)
    elif abs(int(result) - result) - abs(math.ceil(result) - result) < 0.3:
        return int(result)
    else:
        return math.ceil(result)

def get_white_line_length_x(img):
    image = cv2.imdecode(numpy.fromfile(img, dtype=numpy.uint8), 1)
    shape = image.shape
    height = shape[0]
    width = shape[1]
    # print()
    REDISPLAY_PERCENT_R_G_B = TFile.load_config("RedisplayPercentRGB")
    R = REDISPLAY_PERCENT_R_G_B[0]
    G = REDISPLAY_PERCENT_R_G_B[1]
    B = REDISPLAY_PERCENT_R_G_B[2]
    end = 0
    for i in range(int(width / 2), width):
        if image[int(height / 2), i, 0] < R and image[int(height / 2), i, 0] < G and image[int(height / 2), i, 0] < B:
            end = i


def set_picture_text(text,image):
    """ 图片加文本 """
    bk_img = cv2.imread(image)
  
    #在图片上添加文字信息
    cv2.putText(bk_img,text, (350,100), cv2.FONT_HERSHEY_TRIPLEX,1,(0, 0, 255), 2, 10)
    #保存图片
    file = TFile.get_cache_picture(keyword = "Log")
    cv2.imwrite(file,bk_img)
    
    return file

def set_picture_split(image1,image2):
    """ 图像拼接"""
    image1 = cv2.imread(image1) 
    image2 = cv2.imread(image2) 
    # image1 = cv2.resize(image1, (700, 480 * 1))
    # image2 = cv2.resize(image2, (700, 480 * 1))

    #verticalAppendedImg = numpy.vstack((image1,image2))
    horizontalAppendedImg = numpy.hstack((image1,image2))
    # cv2.imshow('Vertical Appended', verticalAppendedImg)
    # #cv2.imshow('Horizontal Appended', horizontalAppendedImg)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    file = TFile.get_cache_picture(keyword = "Log")
    cv2.imwrite(file,horizontalAppendedImg)
    return file





def get_video_status(video_name):
    cap = cv2.VideoCapture(video_name)
    cnt = 0
    static = 0
    max_static = 0
    blue_screen_count = 0
    black_screen_count = 0
    green_screen_count = 0
    white_screen_count = 0
    continuous_jamming_frame = 0
    img_list = []
    while cap.isOpened():
        cnt += 1
        ret, frame = cap.read()
        if not ret:
            break
        if cnt % 30 == 0:
            filename = TFile.get_cache_picture("VideoSS")
            cv2.imencode(".png", frame)[1].tofile(filename)
            img_list.append(filename)
            if len(img_list) > 1:
                if get_image_similarity(img_list[-1], img_list[-2], 96):
                    static += 1
                    continuous_jamming_frame += 1
                    if continuous_jamming_frame > max_static:
                        max_static = continuous_jamming_frame
                    TLog.api_warning("StaticScreen, image1=%s, image2=%s" % (img_list[-1], img_list[-2]))
                else:
                    continuous_jamming_frame = 0
        (b, g, r) = cv2.split(frame)
        b_avg, b_min, b_max, b_std = numpy.mean(b), numpy.min(b), numpy.max(b), numpy.std(b)
        g_avg, g_min, g_max, g_std = numpy.mean(g), numpy.min(g), numpy.max(g), numpy.std(g)
        r_avg, r_min, r_max, r_std = numpy.mean(r), numpy.min(r), numpy.max(r), numpy.std(r)
        if numpy.max([b_std, g_std, r_std]) < 8:
            # 纯色图片
            if b_min >= 64 and r_avg < (255 - 3 * r_avg) / 255 * b_avg and g_avg <= b_avg * b_avg / 255:
                blue_screen_count += 1
                TLog.api_warning("BlueScreen, FPS=%d" % cnt)
            elif g_min >= 64 and numpy.max([b_avg, r_avg]) < g_avg * (1 - g_avg / 510) and numpy.max(
                    [b_avg, r_avg]) < g_avg - 48:
                green_screen_count += 1
                TLog.api_warning("GreenScreen, FPS=%d" % cnt)
            elif numpy.mean([b_avg, g_avg, r_avg]) < 64 and numpy.max([b_max, g_max, r_max]) < 80:
                black_screen_count += 1
                TLog.api_warning("BlackScreen, FPS=%d" % cnt)
            elif numpy.mean([b_avg, g_avg, r_avg]) > 215 and numpy.min([b_min, g_min, r_min]) > 199:
                white_screen_count += 1
                TLog.api_warning("WhiteScreen, FPS=%d" % cnt)
    cap.release()
    if static > 1:
        TLog.api_error("视频画面中出现卡顿(计数=%d, 最大连续卡帧=%d)" % (static, max_static))
    if blue_screen_count > 1:
        TLog.api_error("视频画面中出现蓝屏(计数=%d)" % blue_screen_count)
    if black_screen_count > 1:
        TLog.api_error("视频画面中出现黑屏(计数=%d)" % black_screen_count)
    if green_screen_count > 1:
        TLog.api_error("视频画面中出现绿屏(计数=%d)" % green_screen_count)
    if white_screen_count > 1:
        TLog.api_error("视频画面中出现白屏(计数=%d)" % white_screen_count)
    if numpy.max([static, blue_screen_count, black_screen_count, green_screen_count, white_screen_count]) > 1:
        return False
    return True



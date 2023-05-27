import cv2
 
# 读取图片
baseImg = cv2.imread("0407141748.928169.png")
curImg= cv2.imread("0407140045.254668.png")
# 转灰度图
gray_base = cv2.cvtColor(baseImg, cv2.COLOR_BGR2GRAY)
gray_cur = cv2.cvtColor(curImg, cv2.COLOR_BGR2GRAY)
     
resImg = cv2.absdiff(gray_cur, gray_base)

# threshold阈值函数(原图像应该是灰度图,对像素值进行分类的阈值,当像素值高于（有时是小于）阈值时应该被赋予的新的像素值,阈值方法)
thresh = cv2.threshold(resImg, 30, 255, cv2.THRESH_BINARY)[1]
 # 用一下腐蚀与膨胀
thresh = cv2.dilate(thresh, None, iterations=2)
 # findContours检测物体轮廓(寻找轮廓的图像,轮廓的检索模式,轮廓的近似办法)
contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
for c in contours:
  # 设置敏感度
  # contourArea计算轮廓面积
  if cv2.contourArea(c) > 1000:
    print('#####',cv2.contourArea(c))



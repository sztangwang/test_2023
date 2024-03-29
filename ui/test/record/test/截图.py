import pyautogui
import cv2
import numpy as np
 
img = pyautogui.screenshot(region=[300,50, 500, 600])  # 分别代表：左上角坐标，宽高
#对获取的图片转换成二维矩阵形式，后再将RGB转成BGR
#因为imshow,默认通道顺序是BGR，而pyautogui默认是RGB所以要转换一下，不然会有点问题
img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
 
cv2.imshow("截屏",img)
cv2.waitKey(0)
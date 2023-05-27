# -*- coding:utf-8 -*-
#! python3
from PIL import Image
i = 1
j = 1
img = Image.open("00000019.jpg")#读取系统的内照片

width = img.size[0]#长度
height = img.size[1]#宽度
for i in range(0,width):#遍历所有长度的点
  for j in range(0,height):#遍历所有宽度的点
    data = (img.getpixel((i,j)))#打印该图片的所有点
    if (abs(data[0] - 220) > 20 or abs(data[1] - 76) > 20 or abs(data[2] - 60) > 20):#RGBA的r值大于170，并且g值大于170,并且b值大于170
      img.putpixel((i,j),(0,0,0,0))#则这些像素点的颜色改成大红色
img = img.convert("RGB")#把图片强制转成RGB
img.save("D:\\testee1.jpg")#保存修改像素点后的图片


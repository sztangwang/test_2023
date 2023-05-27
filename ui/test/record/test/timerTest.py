import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ann = np.array(Image.open("00000019.jpg"))

# 分别过滤 通道 R, G, B
#red_filtered = (ann[:, :, :] > (200, 70, 70))
# 在提取一定范围的颜色时，可以将 == 调整为 < 或 >
red_filtered = (ann[:, :, 0]>200)&(ann[:, :, 1]>60)&(ann[:, :, 2]>60)
red = ann.copy()
# red[:, :, :] = red[:, :, :] * red_filtered
#red[:, :, 0] = red[:, :, 0] * red_filtered
#red[:, :, 1] = red[:, :, 1] * red_filtered
red[:, :, 2] = red[:, :, 2] * red_filtered
plt.imshow(red)
plt.show()
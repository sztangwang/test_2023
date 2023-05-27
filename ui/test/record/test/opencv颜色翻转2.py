import cv2
import numpy as np

img = cv2.imread('00000019.jpg')

ret, mask = cv2.threshold(img[:, :,2], 200, 255, cv2.THRESH_BINARY)

mask3 = np.zeros_like(img)
mask3[:, :, 0] = mask
mask3[:, :, 1] = mask
mask3[:, :, 2] = mask

# extracting `orange` region using `biteise_and`
orange = cv2.bitwise_and(img, mask3)



cv2.imwrite('orange.png', orange)

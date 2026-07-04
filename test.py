import cv2
import os

path = r"uploads\test.jpg"   # uploads içine elle bir jpg koy

print(os.path.exists(path))

img = cv2.imread(path)

print(img is None)
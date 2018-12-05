import cv2

map = cv2.imread(r'C:\Users\kengo\Documents\api-assets\Assets\Maps\Erangel_Main_Low_Res.jpg')
h,w,c = map.shape
print(str(h)+","+str(w))
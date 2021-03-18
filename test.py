import pytesseract
from PIL import Image
import cv2

zh_img = r'D:\code\mcms\app\static\upload\perview\2021\3\10\ig\112969.jpg'
im = cv2.imread(zh_img)
im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
cv2.imwrite(im_gray,r'D:\112969.jpg')
zh = pytesseract.image_to_string(im_gray, lang="chi_sim").strip()
if zh:
    print(zh)
else:
    print('noting')

# cvimg = cv2.imread(zh_img)
# h, w, g = cvimg.shape
# x_start = int(w * 0.25)
# x_end = int(w*0.75)
# y_start = int(h*0.75)
# y_end = int(h*0.95)

# cropped = cvimg[y_start:y_end, x_start:x_end]
# cv2.imwrite(r'D:\105998_x.jpg', cropped)
# zh_img = r'D:\105998_x.jpg'
# zh = pytesseract.image_to_string(Image.open(zh_img), lang="chi_sim").strip()
# if zh:
#     print(zh)
# else:
#     print('noting')

source_dir = r'D:\code\mcms\app\static\upload\perview\2021\3\10\5805cb5f946b5331a32091493de19588'
dec_dir =r'D:\code\mcms\app\static\upload\perview\2021\3\10\ig'
name = 0
# while True:
#     try:
#         zh_img = '{}\\{}.jpg'.format(source_dir, name)
#         print(zh_img)
#         cvimg = cv2.imread(zh_img)
#         h, w, g = cvimg.shape
#         x_start = int(w * 0.25)
#         x_end = int(w*0.75)
#         y_start = int(h*0.75)
#         y_end = int(h*0.95)

#         cropped = cvimg[y_start:y_end, x_start:x_end]
#         cv2.imwrite('{}\\{}.jpg'.format(dec_dir,name), cropped)
#         name += 1
#     except Exception as e:
#         print(str(e))
#         break



# configfile = r'D:\code\mcms\app\static\upload\perview\2021\3\10\file.txt'
# zimu_start = None
# zimu_end = None
# zimu_msg = None
# while True:
#     try:
#         zh_img = '{}\\{}.jpg'.format(dec_dir, name)
#         print(zh_img)
#         zh = pytesseract.image_to_string(Image.open(zh_img), lang="chi_sim").strip()
#         if zh:
#             if zimu_start is None:
#                 zimu_start = name
#                 zimu_start = zh
#                 print('获取到开始字幕')
#             else:
#                 if zh != zimu_msg:
#                     zimu_end = name -1
#                     print('获取到结束字幕')
#                     with open(configfile, 'a+') as fr:
#                         fr.write('{} {}'.format(zimu_start,zimu_end))
#                         fr.close()
#                     zimu_start = None
#                     zimu_msg = None
#         else:
#             print('Noting')
#         name += 1
#     except Exception as e:
#         print(str(e))



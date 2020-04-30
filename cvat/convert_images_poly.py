import os
import cv2
import json
import argparse
import xml.dom.minidom

from tqdm import tqdm
from pathlib import Path
from collections import defaultdict

VID_EXTS = ('.mp4', '.avi')
IMG_EXTS = ('.jpg', '.png', '.JPG', '.PNG', '.jpeg', '.JPEG')

parser = argparse.ArgumentParser()
parser.add_argument('--xml', type=str, required=True, help='Path to XML file (CVAT IMAGES)')
parser.add_argument('--root', type=str, required=True, help='Path to folder containing images')
parser.add_argument('--out', type=str, required=True, help='Path to folder to output to')
parser.add_argument('--json', type=str, required=True, help='Path to json describing class mapping')
args = parser.parse_args()

# xml_file = '/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_1.xml'
xml_file = args.xml
ignore_frame_str = 'ignore'
with open(args.json,'r') as f:
    classes_map = json.load(f)
# classes_map = {"ship": 0, "small_ship": 0, "sampan": 0, "big": 0, "small": 0 }


target_class = ["ship"]
# vid_root = '/media/dh/HDD1/pp/Labrador200/trimmed'
img_root = args.root
# sampling_sec = 1 # save one frame every <sampling> seconds.
out_dir = args.out

doc = xml.dom.minidom.parse(xml_file)

source_name = doc.getElementsByTagName("name")[0].childNodes[0].nodeValue
out_dir = os.path.join(out_dir, source_name)
image_out_dir = os.path.join(out_dir, 'images')

if not os.path.isdir(image_out_dir):
    os.makedirs(image_out_dir)
viz_out_dir = os.path.join(out_dir, 'viz')
if not os.path.isdir(viz_out_dir):
    os.makedirs(viz_out_dir)
# annot_dettrack_out = os.path.join(out_dir, 'annot_det_track.txt')
annot_det_out = os.path.join(out_dir, 'annot_det.part.txt')

annot_det_write = open(annot_det_out,'w')

imgstem2xmlboxes = {}
for image in doc.getElementsByTagName("image"):
    name = image.getAttribute("name")
    stem = Path(name).stem
    stem = stem.replace(' ','-')

    boxes = []

    for box in image.getElementsByTagName("box"):
        label = box.getAttribute("label")
        l = int(float(box.getAttribute("xtl")))
        t = int(float(box.getAttribute("ytl")))
        r = int(float(box.getAttribute("xbr")))
        b = int(float(box.getAttribute("ybr")))
        boxes.append([l,t,r,b], label)

    for polygon in image.getElementsByTagName("polygon"):
        points_str = polygon.getAttribute("points")
        points = []
        for pairs in points_str.split(';'):
            x, y = pairs.split(',')
            points.append((int(float(x)), int(float(y))))

        if len(points) > 0:
            x_min = min(points, key= lambda t: t[0])[0]
            x_max = max(points, key= lambda t: t[0])[0]
            y_min = min(points, key= lambda t: t[1])[1]
            y_max = max(points, key= lambda t: t[1])[1]
            bb = [x_min, y_min, x_max, y_max]
            label = polygon.getAttribute("label")
            boxes.append((bb, label))

    imgstem2xmlboxes[stem] = boxes

ignore_count = 0
for impath in tqdm(Path(img_root).rglob('*')):
    if not str(impath).endswith(IMG_EXTS):
        continue
    ignore = False
    stem = impath.stem
    img = cv2.imread(str(impath))
    viz_frame = img.copy()

    annot_det_segs = []

    if stem in imgstem2xmlboxes:
        for box in imgstem2xmlboxes[stem]:
            ltrb, label = box
            # label = box.getAttribute("label")
            if label == ignore_frame_str:
                ignore = True
                ignore_count += 1
                break

            if label not in classes_map:
                print('[WARNING] LABEL {} IS NOT FOUND IN CLASSES_MAP'.format(label))
                continue
            cid = classes_map[label]
            l,t,r,b = ltrb
            # l = float(box.getAttribute("xtl"))
            # t = float(box.getAttribute("ytl"))
            # r = float(box.getAttribute("xbr"))
            # b = float(box.getAttribute("ybr"))
            # l,t,r,b = [int(x) for x in [l,t,r,b]]
            cv2.rectangle(viz_frame, (l,t), (r,b), (100,255,0), 2)
            cv2.putText(viz_frame, '{}'.format(target_class[cid]), (l+5, b-10), cv2.FONT_HERSHEY_DUPLEX, 1.0, (100,255,0), 1)
            annot_det_segs.append(" {},{},{},{},{}".format(l,t,r,b,cid))

    if ignore:
        continue

    annot_det_write.write("{}.png".format(stem))
    for s in annot_det_segs:
        annot_det_write.write(s)
    annot_det_write.write("\n")

    cv2.imwrite(os.path.join(image_out_dir, '{}.png'.format(stem)), img)
    cv2.imwrite(os.path.join(viz_out_dir, '{}.jpg'.format(stem)), viz_frame)

annot_det_write.close()
print('Ignored: {}'.format(ignore_count))

# for image in tqdm(doc.getElementsByTagName("image")):
#     ignore = False
#     id_ = image.getAttribute("id")
#     name = image.getAttribute("name")
#     impath = Path(img_root) / name
#     assert impath.is_file(),'{}'.format(impath) 
#     stem = impath.stem

#     iw = image.getAttribute("width")
#     ih = image.getAttribute("height")

#     img = cv2.imread(str(impath))
#     viz_frame = img.copy()

#     annot_det_segs = []
#     for box in image.getElementsByTagName("box"):
#         label = box.getAttribute("label")
#         if label == ignore_frame_str:
#             ignore=True
#             break
#         cid = classes_map[label]
#         l = float(box.getAttribute("xtl"))
#         t = float(box.getAttribute("ytl"))
#         r = float(box.getAttribute("xbr"))
#         b = float(box.getAttribute("ybr"))
#         l,t,r,b = [int(x) for x in [l,t,r,b]]
#         cv2.rectangle(viz_frame, (l,t), (r,b), (100,255,0), 2)
#         cv2.putText(viz_frame, '{}'.format(target_class[cid]), (l+5, b-10), cv2.FONT_HERSHEY_DUPLEX, 1.0, (100,255,0), 1)
#         annot_det_segs.append(" {},{},{},{},{}".format(l,t,r,b,cid))

#     if ignore:
#         continue

#     annot_det_write.write("{}.png".format(stem))
#     for s in annot_det_segs:
#         annot_det_write.write(s)
#     annot_det_write.write("\n")

#     cv2.imwrite(os.path.join(image_out_dir, '{}.png'.format(stem)), img)
#     cv2.imwrite(os.path.join(viz_out_dir, '{}.jpg'.format(stem)), viz_frame)


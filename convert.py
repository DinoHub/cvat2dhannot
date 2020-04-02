import os
import cv2
import xml.dom.minidom
import argparse

from pathlib import Path
from collections import defaultdict

VID_EXTS = ('.mp4', '.avi')

parser = argparse.ArgumentParser()
parser.add_argument('--xml', type=str, required=True, help='Path to XML file')
parser.add_argument('--root', type=str, required=True, help='Path to folder containing video file')
parser.add_argument('--out', type=str, required=True, help='Path to folder to output to')
parser.add_argument('--sample', type=float, help='sample every x number of seconds', default=1)
args = parser.parse_args()

# xml_file = '/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_1.xml'
xml_file = args.xml
classes_map = {"ship": 0, "small_ship": 0, "sampan": 0 }
target_class = ["ship"]
# vid_root = '/media/dh/HDD1/pp/Labrador200/trimmed'
vid_root = args.root
# sampling_sec = 1 # save one frame every <sampling> seconds.
sampling_sec = float(args.sample) # save one frame every <sampling> seconds.
out_dir = args.out

doc = xml.dom.minidom.parse(xml_file)

source_vid = doc.getElementsByTagName("source")[0].childNodes[0].nodeValue
vid_name,_ = os.path.splitext(os.path.basename(source_vid))
out_dir = os.path.join(out_dir, vid_name)
image_out_dir = os.path.join(out_dir, 'images')
if not os.path.isdir(image_out_dir):
    os.makedirs(image_out_dir)
viz_out_dir = os.path.join(out_dir, 'viz')
if not os.path.isdir(viz_out_dir):
    os.makedirs(viz_out_dir)
annot_dettrack_out = os.path.join(out_dir, 'annot_det_track.txt')
annot_det_out = os.path.join(out_dir, 'annot_det.txt')

annot_dict = defaultdict(list) 
for track in doc.getElementsByTagName("track"):
    label = track.getAttribute("label")
    # if label in wanted_classes:
    # if label == ignore_str:
    #     ignore_frames.append(frame)
    if label in classes_map.keys():
        # class_idx = wanted_classes.index(label)
        class_idx = classes_map[label]
    else:
        print('[WARNING] LABEL {} IS NOT FOUND IN CLASSES_MAP'.format(label))
        continue
    track_id = int(track.getAttribute("id"))
    for box in track.getElementsByTagName("box"):
        outside = bool(int(box.getAttribute("outside")))
        if outside:
            continue
        frame = int(box.getAttribute("frame"))
        keyframe = bool(int(box.getAttribute("keyframe")))
        xtl = float(box.getAttribute("xtl"))
        ytl = float(box.getAttribute("ytl"))
        xbr = float(box.getAttribute("xbr"))
        ybr = float(box.getAttribute("ybr"))
        annot_dict[frame].append([xtl, ytl, xbr, ybr, class_idx, track_id])

for vp in Path(vid_root).glob('*'):
    if vp.name.endswith(VID_EXTS):
        if vid_name in vp.name:
            vid_path = str(vp)
# vid_path = os.path.join(vid_root, source_vid)

cap = cv2.VideoCapture(vid_path)
print('Video file {} is opened:{}'.format(vid_path, cap.isOpened()))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('Total frames: {}'.format(total_frames))
vid_fps = cap.get(cv2.CAP_PROP_FPS)
print('Vid FPS: {}'.format(vid_fps))
if sampling_sec == 0:
    sampling_num = 1
else:
    sampling_num = int(vid_fps * sampling_sec)
sampled_frame_idxes = []
annot_dettrack_write = open(annot_dettrack_out,'w')
annot_det_write = open(annot_det_out,'w')
frame_idx = -1
while True:
    ret, frame = cap.read()
    if not ret:
        break
    else:
        frame_idx += 1
    if frame_idx%sampling_num != 0:
        continue
    print('Frame: {}'.format(frame_idx))
    cv2.imwrite(os.path.join(image_out_dir, '{}.png'.format(frame_idx)), frame)
    sampled_frame_idxes.append(frame_idx)

    if len(annot_dict[frame_idx]) > 0:
        annot_dettrack_write.write("{}.png".format(frame_idx))
        annot_det_write.write("{}.png".format(frame_idx))

    viz_frame = frame.copy()
    for box in annot_dict[frame_idx]:
        l,t,r,b,cid,tid = box 
        l,t,r,b = [int(x) for x in [l,t,r,b]]
        cv2.rectangle(viz_frame, (l,t), (r,b), (100,255,0), 2)
        cv2.putText(viz_frame, '{}-{}'.format(target_class[cid], tid), (l+5, b-10), cv2.FONT_HERSHEY_DUPLEX, 1.0, (100,255,0), 1)
        annot_dettrack_write.write(" {},{},{},{},{},{}".format(l,t,r,b,cid,tid))
        annot_det_write.write(" {},{},{},{},{}".format(l,t,r,b,cid))
    
    if len(annot_dict[frame_idx]) > 0:
        annot_dettrack_write.write(';\n')
        annot_det_write.write(';\n')
    cv2.imwrite(os.path.join(viz_out_dir, '{}.jpg'.format(frame_idx)), viz_frame)

annot_dettrack_write.close()
annot_det_write.close()
cap.release()
import os
import cv2
import xml.dom.minidom
import argparse

from pathlib import Path
from collections import defaultdict

VID_EXTS = ('.mp4', '.avi')

def within_range(current, limits):
    if limits[0] <= current <= limits[1]:
        return True
    else:
        return False

parser = argparse.ArgumentParser()
parser.add_argument('--xml', type=str, required=True, help='Path to XML file')
parser.add_argument('--root', type=str, required=True, help='Path to folder containing video file')
# parser.add_argument('--sample', type=float, help='sample every x number of seconds', default=1)
args = parser.parse_args()

ORANGE = (0,165,255)
GREEN = (50,205,50)
MAGENTA = (255,0,255)

valid_frames = (3380, 3530)

target_tid = 96
target_orange_frames = (3416, 3471)
target_green_frames = (3472, 3530)

# ship_12_color = MAGENTA
# ship_14_color = MAGENTA
# ship_15_color = MAGENTA
# ship_20_color = MAGENTA

# xml_file = '/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_1.xml'
xml_file = args.xml
wanted_classes = ["ship"]
# vid_root = '/media/dh/HDD1/pp/Labrador200/trimmed'
vid_root = args.root
# sampling_sec = 1 # save one frame every <sampling> seconds.
# sampling_sec = float(args.sample) # save one frame every <sampling> seconds.

doc = xml.dom.minidom.parse(xml_file)

source_vid = doc.getElementsByTagName("source")[0].childNodes[0].nodeValue
vid_name,_ = os.path.splitext(os.path.basename(source_vid))

annot_dict = defaultdict(list) 
for track in doc.getElementsByTagName("track"):
    label = track.getAttribute("label").lower()
    if label in wanted_classes:
        class_idx = wanted_classes.index(label)
    else:
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

vids = os.listdir(vid_root)
for vid in vids:
    if vid_name in vid:
        source_vid = vid

for vp in Path(vid_root).glob('*'):
    if vp.name.endswith(VID_EXTS):
        if vid_name in vp.name:
            vid_path = str(vp)
# vid_path = os.path.join(vid_root, source_vid)
cap = cv2.VideoCapture(vid_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print('Total frames: {}'.format(total_frames))
vid_fps = cap.get(cv2.CAP_PROP_FPS)
vid_width = int(cap.get(3))
vid_height = int(cap.get(4))
print('Vid FPS: {} Vid Width: {} Vid Height: {}'.format(vid_fps, vid_width, vid_height))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
if not os.path.exists('vids'):
    os.makedirs('vids')
out_vid = cv2.VideoWriter(os.path.join(os.getcwd(),
    'vids', 'forxp_output.mp4'), fourcc, int(vid_fps), (vid_width, vid_height))

# if sampling_sec == 0:
#     sampling_num = 1
# else:
#     sampling_num = int(vid_fps * sampling_sec)
sampled_frame_idxes = []
frame_idx = -1
while True:
    ret, frame = cap.read()
    if not ret:
        break
    else:
        frame_idx += 1
    # if frame_idx%sampling_num != 0:
        # continue
    if not within_range(frame_idx, valid_frames):
        continue 
    if frame_idx > valid_frames[1]:
        break

    print('Frame: {}'.format(frame_idx))
    
    # sampled_frame_idxes.append(frame_idx)

    viz_frame = frame.copy()

    for box in annot_dict[frame_idx]:
        l,t,r,b,cid,tid = box 
        l,t,r,b = [int(x) for x in [l,t,r,b]]
        if tid == target_tid and within_range(frame_idx, target_orange_frames):
            cv2.rectangle(viz_frame, (l,t), (r,b), ORANGE, 2)
        elif tid == target_tid and within_range(frame_idx, target_green_frames):
            cv2.rectangle(viz_frame, (l,t), (r,b), GREEN, 2)
            if frame_idx == target_green_frames[0]:
                for buff in range(0, 50, 5):
                    out_crop = frame.copy()[t-buff:b+1+buff, l-buff:r+1+buff]
                    cv2.imwrite('cropped_chip_buff{}.png'.format(buff), out_crop)        
        else:
            cv2.rectangle(viz_frame, (l,t), (r,b), MAGENTA, 2)
        # cv2.putText(viz_frame, '{}-{}'.format(wanted_classes[cid], tid), (l+5, b-10), cv2.FONT_HERSHEY_DUPLEX, 1.0, (100,255,0), 1)
    # cv2.imshow('', viz_frame)
    # cv2.waitKey(0)
    # if cv2.waitKey(1) == ord('q'):
    #     break 
    out_vid.write(viz_frame)
cap.release()


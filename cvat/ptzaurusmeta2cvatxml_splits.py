import argparse
import numpy as np
import xml.etree.ElementTree as ET

from tqdm import tqdm
from pathlib import Path
from collections import defaultdict

CLASSES = ['ship']
parser = argparse.ArgumentParser()
parser.add_argument(
    "meta_file", help="Path to meta file containing predictions", type=str
)
parser.add_argument(
    "--splitsof", help='Frames are split in batches of [splitsof]', type=int
)
args = parser.parse_args()

meta_file_path = Path(args.meta_file)
assert meta_file_path.is_file()

with meta_file_path.open() as f:
    lines = f.readlines()

bb_count = 0
imgnames = []
track_ids = []
track_idx2bbs = defaultdict(list)
track_idx2classes = defaultdict(list)
for line in lines:
    splits = line.split(' ')
    imgname = splits[0]
    if imgname not in imgnames:
        imgnames.append(imgname)
    bbs = splits[1:]
    for bb in bbs:
        bb_count += 1
        l,t,r,b,class_idx,track_id,bigsmall_val = bb.split(',')
        pred = [[float(l),float(t),float(r),float(b)], CLASSES[int(class_idx)], track_id ]
        if track_id not in track_ids:
            track_ids.append(track_id)
        track_idx = track_ids.index(track_id)
        track_idx2bbs[track_idx].append([imgname, l, t, r, b])
        track_idx2classes[track_idx].append(CLASSES[int(class_idx)])

sorted_imgnames = sorted(imgnames, key=lambda x: int(x.split('_')[-1].split('.')[0]))
# print(sorted_imgnames)

track_idx2frameIdxLimits = {}
for track_idx, bbs in track_idx2bbs.items():
    min_frame_idx = np.inf
    max_frame_idx = -1
    for bb in bbs:
        imgname = bb[0]
        frame_idx = sorted_imgnames.index(imgname)
        if frame_idx > max_frame_idx:
            max_frame_idx = frame_idx
        if frame_idx < min_frame_idx:
            min_frame_idx = frame_idx
    limits = (min_frame_idx, max_frame_idx)
    track_idx2frameIdxLimits[track_idx] = limits

# XML WRITING
# intro
if args.splitsof and args.splitsof > 0:
    split_bs = args.splitsof
    num_splits = len(sorted_imgnames) // split_bs + 1
else:
    split_bs = len(sorted_imgnames)
    num_splits = 1

print('Splitting into {} batches of {} each (other than the last one)'.format(num_splits, split_bs))


# for i in range(num_splits):
for i_split, k in enumerate(range(0, len(sorted_imgnames), split_bs)):
    xml_data = ET.Element('annotations')
    version = ET.SubElement(xml_data, 'version')
    version.text = '1.1'

    from_frame_idx = k
    to_frame_idx = k + split_bs - 1
    print('Parsing from frames {} to {}'.format(from_frame_idx, to_frame_idx))

    # Writing the actual stuffs
    box_props = ['frame', 'outside', 'occluded', 'keyframe', 'xtl', 'ytl', 'xbr','ybr']
    outside = 0
    occluded = 0
    keyframe = 1
    for track_idx, track_id in enumerate(track_ids):
        # check limits first
        limits = track_idx2frameIdxLimits[track_idx]
        if limits[0] > to_frame_idx or limits[1] < from_frame_idx:
            continue

        track_xml_element = ET.SubElement(xml_data, 'track')
        track_xml_element.set('id', str(track_idx))
        classes = track_idx2classes[track_idx]
        mode_class = max(set(classes), key=class_idx.count) # the class that appear the most in the track
        track_xml_element.set('label', mode_class)
        last_frame_idx = -1
        for box in track_idx2bbs[track_idx]:
            imgname, l, t, r, b = box
            curr_frame_idx = sorted_imgnames.index(imgname)
            if curr_frame_idx < from_frame_idx or curr_frame_idx > to_frame_idx:
                continue

            box_xml_element = ET.SubElement(track_xml_element, 'box')
            box_xml_element.text = " "

            res = [ curr_frame_idx, outside, occluded, keyframe, l, t, r, b ]
            if curr_frame_idx > last_frame_idx:
                last_frame_idx = curr_frame_idx
            for prop, val in zip(box_props, res):
                # print('Setting {} as {}'.format(prop, val))
                box_xml_element.set(prop, str(val))

            # attrib_xml_element = ET.SubElement(box_xml_element, 'attribute')
            # attrib_xml_element.set('name', 'sensor')
            # attrib_xml_element.text = 'flir'

        # CVAT has a weird quirk, we need to 'end' a track by having an "outside=1" box at the next frame, the other properties of the box does not matter at all
        last_last_frame_idx = last_frame_idx + 1
        if last_last_frame_idx >= len(sorted_imgnames):
            continue
        if last_last_frame_idx < from_frame_idx or last_last_frame_idx > to_frame_idx:
            continue

        end_box_element = ET.SubElement(track_xml_element, 'box')
        end_box_element.text = " "
        imgname, l, t, r, b = box
        res = [ last_last_frame_idx, 1, occluded, keyframe, l, t, r, b ]
        for prop, val in zip(box_props, res):
            # print('Setting {} as {}'.format(prop, val))
            end_box_element.set(prop, str(val))
        # attrib_xml_element = ET.SubElement(end_box_element, 'attribute')
        # attrib_xml_element.set('name', 'sensor')
        # attrib_xml_element.text = 'flir'

    out_file = meta_file_path.parent / '{}_split_{}.xml'.format(meta_file_path.stem, i_split)
    out_file_path = Path(out_file) 
    mydata = ET.tostring(xml_data, encoding='unicode')
    with out_file_path.open(mode="w") as f:
        f.write(mydata)
    print('XML outputed at {}'.format(out_file_path))

print('Total num of frames: {}'.format(len(sorted_imgnames)))
print('Total num of tracks: {}'.format(len(track_ids)))
print('Total num of bbs: {}'.format(bb_count))
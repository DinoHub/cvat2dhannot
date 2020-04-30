import argparse
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict
# from mot_exporter import MOT_exporter

CLASSES = ['ship']

parser = argparse.ArgumentParser()
parser.add_argument(
    "meta_file", help="Path to meta file containing predictions", type=str
)
args = parser.parse_args()

meta_file_path = Path(args.meta_file)
assert meta_file_path.is_file()

out_file = meta_file_path.parent.parent / '{}.csv'.format(meta_file_path.stem)
out_file_path = Path(out_file) 

with meta_file_path.open() as f:
    lines = f.readlines()

imgname2bbs = defaultdict(list)
for line in lines:
    splits = line.split(' ')
    imgname = splits[0]
    bbs = splits[1:]
    for bb in bbs:
        l,t,r,b,class_idx,track_id,bigsmall_val = bb.split(',')
        pred = [[float(l),float(t),float(r),float(b)], CLASSES[int(class_idx)], track_id ]
        imgname2bbs[imgname].append(pred)

sorted_imgnames = sorted(imgname2bbs.keys(), key=lambda x: int(x.split('_')[-1].split('.')[0]))
print(sorted_imgnames)

'''
The MOT CSV format
Frame number (starts from 0), Track id (starts from 0), l, t, w, h, Confidence (default 1.0), Class (in string),Visibility ratio (how much of the object is visible, default is 1.0)
'''
bb_count = 0
track_ids = []
import cv2
img_dir = '/media/dh/HDD/pluggy_archive/2020-03-10T00:07:31:481000'
with out_file_path.open(mode='w') as f:
    for frame_idx, imname in enumerate(sorted_imgnames):
        print(frame_idx, imname)
        impath = Path(img_dir) / imname
        show_frame = cv2.imread(str(impath))
        for pred in imgname2bbs[imname]:
            assert len(pred) == 3
            bb, cl, track_id = pred
            print(track_id)
            color=(255,255,0)
            if track_id not in track_ids:
                track_ids.append(track_id)
                print('added', track_id)
                color=(0,0,255)

            l,t,r,b = bb
            
            w = r - l + 1
            h = b - t + 1

            track_idx = track_ids.index(track_id)
            print('{}: {}'.format(track_id, track_idx))

            write_str = '{},{},{},{},{},{},{},{},{}\n'.format(frame_idx, track_ids.index(track_id), l,t,w,h, 1.0, cl, 1.0 )
            f.write(write_str)
            # print(write_str)
            bb_count += 1
            cv2.rectangle(show_frame, (int(l),int(t)), (int(r),int(b)), color=color, thickness=2)
            cv2.putText(show_frame, '{}:{}'.format(track_id, track_idx+1), (int(l),int(t)), cv2.FONT_HERSHEY_DUPLEX, 1.0, color, thickness=2)

        # cv2.imshow('', show_frame)
        # cv2.waitKey(0)
        cv2.imwrite('{}.png'.format(frame_idx), show_frame)

print(track_ids)
print('Total num of frames: {}'.format(len(sorted_imgnames)))
print('Total num of tracks: {}'.format(len(track_ids)))
print('Total num of bbs: {}'.format(bb_count))
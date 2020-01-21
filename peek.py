import xml.dom.minidom
from collections import defaultdict

xml_file = '/media/dh/HDD1/pp/Labrador200/annotations/trimmed_annotations_1.xml'
wanted_classes = ["ship"]
vid_root = ''

doc = xml.dom.minidom.parse(xml_file)

track_count = 0

annot_dict = defaultdict(list) 
for track in doc.getElementsByTagName("track"):
    label = track.getAttribute("label")
    if label in wanted_classes:
        class_idx = wanted_classes.index(label)
    else:
        continue
    track_id = int(track.getAttribute("id"))
    track_count += 1
    for box in track.getElementsByTagName("box"):
        frame = int(box.getAttribute("frame"))
        keyframe = bool(box.getAttribute("keyframe"))
        xtl = float(box.getAttribute("xtl"))
        ytl = float(box.getAttribute("ytl"))
        xbr = float(box.getAttribute("xbr"))
        ybr = float(box.getAttribute("ybr"))
        annot_dict[frame].append([xtl, ytl, xbr, ybr, class_idx, track_id])

print('Track count: {}'.format(track_count))

source_vid = doc.getElementsByTagName("source")[0].childNodes[0].nodeValue

print(source_vid)

import pdb; pdb.set_trace()
exit()

vid_path = os.path.join(vid_root, source_vid)
cap = cv2.VideoCapture(vid_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
vid_fps = cap.get(cv2.CAP_PROP_FPS)
sampling_num = vid_fps * sampling_sec
sampled_frame_idxes = []
annot_write = open(annot_out,'w')
for frame_idx in range(total_frames):
    ret, frame = cap.read()
    if frame_idx%sampling_num != 0:
        continue
    frame.write(os.path.join(image_out_dir, '{}.png'.format(frame_idx)), frame)
    sampled_frame_idxes.append(frame_idx)
    annot_write.write("{}.png".format(frame_idx))
    viz_frame = frame.copy()
    for box in annot_dict[frame_idx]:
        l,t,r,b,cid,tid = box 
        cv2.rectangle(viz_frame, (l,t), (r,b), (255,255,0), 2)
        cv2.putText(viz_frame, '{}-{}'.format(wanted_classes[cid], tid), (l+5, b-10), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255,255,0), 2)
        annot_write.write(" {},{},{},{},{},{}".format(l,t,r,b,cid,tid))
    annot_write.write(';\n')
    cv2.imwrite(os.path.join(viz_out_dir, '{}.jpg'.format(frame_idx)), viz_frame)

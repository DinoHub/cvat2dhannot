import os
from tqdm import tqdm
from shutil import copy

fof = '/media/dh/HDD1/pp/Labrador200/dh_format'
out_dir = '/media/dh/HDD1/pp/Labrador200/Labrador200_merged'

if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

image_out_dir = os.path.join(out_dir, 'images')
if not os.path.isdir(image_out_dir):
    os.makedirs(image_out_dir)
viz_out_dir = os.path.join(out_dir, 'viz')
if not os.path.isdir(viz_out_dir):
    os.makedirs(viz_out_dir)
annot_dettrack_out = os.path.join(out_dir, 'annot_det_track.txt')
annot_det_out = os.path.join(out_dir, 'annot_det.txt')

bb_count = 0
image_count = 0

def newname(oldname, folder):
    return '{}_{}'.format(folder, oldname)

old_max_tid = -1
for folder in tqdm(os.listdir(fof)):
    images_dir = os.path.join(fof, folder, 'images')
    for image in os.listdir(images_dir):
        ip = os.path.join(images_dir, image)
        new_ip = os.path.join(image_out_dir, newname(image, folder))
        # print('Copy from {} to {}'.format(ip, new_ip))
        copy(ip, new_ip)
        image_count += 1
    viz_dir = os.path.join(fof, folder, 'viz')
    for viz in os.listdir(viz_dir):
        ip = os.path.join(viz_dir, viz)
        new_ip = os.path.join(viz_out_dir, newname(viz, folder))
        # print('Copy from {} to {}'.format(ip, new_ip))
        copy(ip, new_ip)
    max_tid = -1
    with open(os.path.join(fof,folder,'annot_det_track.txt'),'r') as oldf:
        with open(annot_dettrack_out, 'a') as newf:
            for line in oldf.readlines():
                splits = line.strip().replace(';','').split(' ')
                splits[0] = newname(splits[0], folder)
                
                new_bbs = []
                # print('old max tid: ', old_max_tid)
                for bb in splits[1:]:
                    bbsplits = bb.split(',')
                    tid = int(bbsplits[-1])
                    # print('old_tid',tid)
                    tid = (old_max_tid + 1) + tid 
                    # print('new_tid',tid)
                    max_tid = max(max_tid, tid)
                    bbsplits[-1] = str(tid)
                    bb = ','.join(bbsplits)
                    new_bbs.append(bb)
                # print('new max tid', max_tid)
                splits[1:] = new_bbs

                newline = ' '.join(splits)
                newf.write(newline+';\n')
    old_max_tid = max_tid

    with open(os.path.join(fof,folder,'annot_det.txt'),'r') as oldf:
        with open(annot_det_out, 'a') as newf:
            for line in oldf.readlines():
                splits = line.split(' ')
                bb_count += (len(splits)-1)
                splits[0] = newname(splits[0], folder)
                newline = ' '.join(splits)
                newf.write(newline)

image_count_text = 'Total image count: {}'.format(image_count)
bb_count_text = 'Total bb count: {}'.format(bb_count)  
with open(os.path.join(out_dir,'meta.txt'), 'w') as f:
    f.write(image_count_text+'\n')
    f.write(bb_count_text)
print(image_count_text)
print(bb_count_text)
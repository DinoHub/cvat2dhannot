import os
from shutil import copy

fof = '/media/dh/HDD1/pp/Labrador200/dh_format'
out_dir = '/media/dh/HDD1/pp/Labrador200/merged_dataset'

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

def newname(oldname, folder):
    return '{}_{}'.format(folder, oldname)

for folder in os.listdir(fof):
    images_dir = os.path.join(fof, folder, 'images')
    for image in os.listdir(images_dir):
        ip = os.path.join(images_dir, image)
        new_ip = os.path.join(image_out_dir, newname(image, folder))
        # print('Copy from {} to {}'.format(ip, new_ip))
        copy(ip, new_ip)
    viz_dir = os.path.join(fof, folder, 'viz')
    for viz in os.listdir(viz_dir):
        ip = os.path.join(viz_dir, viz)
        new_ip = os.path.join(viz_out_dir, newname(viz, folder))
        # print('Copy from {} to {}'.format(ip, new_ip))
        copy(ip, new_ip)
    with open(os.path.join(fof,folder,'annot_det_track.txt'),'r') as oldf:
        with open(annot_dettrack_out, 'a') as newf:
            for line in oldf.readlines():
                splits = line.split(' ')
                splits[0] = newname(splits[0], folder)
                newline = ' '.join(splits)
                newf.write(newline)

    with open(os.path.join(fof,folder,'annot_det.txt'),'r') as oldf:
        with open(annot_det_out, 'a') as newf:
            for line in oldf.readlines():
                splits = line.split(' ')
                splits[0] = newname(splits[0], folder)
                newline = ' '.join(splits)
                newf.write(newline)

import os 
from tqdm import tqdm
import random
from PIL import Image


# mother dir, geddit??? modir.
modir = '/media/dh/DATA4TB/Datasets/pp_modir'

train_split = 0.8
max_height = 0.5
annot_fps = [
# '/media/dh/DATA4TB/Datasets/VOCdevkit/VOC2012/boat_trainval_contexted.txt',
# '/home/dh/Workspace/coco_splitter/coco_boat_contexted_annot.txt',
# '/home/dh/Workspace/openimages_splitter/openimages_boat_contexted_annot.txt'
            ]

annot_fps_presplit_train = [
'/media/dh/DATA4TB/Datasets/SGMaritimeDataset/SMD_train_contexted.txt',
'/media/dh/DATA4TB/Datasets/SeaShips7000/train_contexted.txt',
'/media/dh/DATA4TB/Datasets/SeaShips7000/test_contexted.txt'
                    ]
annot_fps_presplit_val = [
'/media/dh/DATA4TB/Datasets/SGMaritimeDataset/SMD_val_contexted.txt',
'/media/dh/DATA4TB/Datasets/SeaShips7000/val_contexted.txt'
                    ]

mother_annot_fps = [(fp, None) for fp in annot_fps]
mother_annot_fps += [(fp, True) for fp in annot_fps_presplit_train]
mother_annot_fps += [(fp, False) for fp in annot_fps_presplit_val]

if not os.path.isdir(modir):
    os.makedirs(modir)
assert os.path.isdir(modir)

modir_images = os.path.join(modir, 'images')
if not os.path.isdir(modir_images):
    os.makedirs(modir_images)
assert os.path.isdir(modir_images)

modir_label = os.path.join(modir, 'labels')
if not os.path.isdir(modir_label):
    os.makedirs(modir_label)
assert os.path.isdir(modir_label)

train_list = []
val_list = []
failed_list = []

mother_train = 0
mother_val = 0
for fp, trainvalflag in mother_annot_fps:
    independent_train_count = 0
    independent_val_count = 0
    assert os.path.exists(fp), '{} does not exist'.format(fp)
    with open (fp,'r') as f:
        this_lines = f.readlines()
    
    random.shuffle(this_lines)
    this_total_imgs = len(this_lines)
    train_count = int(train_split*this_total_imgs)
    img_idx = 0

    for line in tqdm(this_lines):
        split = line.strip().replace(';','').split()
        img_path = split[0]
        assert os.path.exists(img_path)
        im = Image.open(img_path)
        iw, ih = im.size
        bbs = split[1:]
        #x_min,y_min,x_max,y_max,class_id
        txt_strs = []
        is_too_big = False
        for bb in bbs:
            x_min, y_min, x_max, y_max, class_id = [int(x) for x in bb.split(',')]

            w = x_max - x_min + 1
            h = y_max - y_min + 1
            cx = x_min + w/2 - 1
            cy = y_min + h/2 - 1
            
            ncx = cx / iw
            ncy = cy / ih
            nw = w / iw
            nh = h / ih

            if nh > max_height:
                is_too_big = True
                break

            txt_strs.append('{} {} {} {} {}\n'.format(class_id, ncx, ncy, nw, nh))

        img_basename = os.path.basename(img_path)
        basename = img_basename.split('.')[0]


        if is_too_big:
            # print('{} is too big'.format(img_path))
            this_total_imgs -= 1
            train_count = int(train_split * this_total_imgs )
            failed_list.append(img_path+'\n')
            # if os.path.exists(final_symlink_path):
            #     os.remove(final_symlink_path)
            continue

        final_symlink_path = os.path.join(modir_images,img_basename)
        rel_impath = os.path.relpath(img_path, modir_images) 

        if os.path.exists(final_symlink_path):
            assert os.readlink(final_symlink_path) == rel_impath,'Conflict of symlink path: Current symlink path {} you are trying to create already has a symlink to another file at {}'.format(final_symlink_path, rel_impath)
        else:
            os.symlink(rel_impath,final_symlink_path)

        txt_fp = os.path.join(modir_label, '{}.txt'.format(basename))
        with open(txt_fp,'w') as f:
            f.writelines(txt_strs)

        # dice = random.uniform(0,1)
        # if dice > train_split:
        if (trainvalflag is None and img_idx < train_count) or trainvalflag:
            train_list.append(final_symlink_path+'\n')
            independent_train_count += 1
        else:
            val_list.append(final_symlink_path+'\n')
            independent_val_count += 1
        img_idx += 1

    print('Dataset: {}'.format( os.path.join(*fp.split('/')[-2:]) ))
    print('\t#train images: {}'.format(independent_train_count))
    print('\t#val images: {}'.format(independent_val_count))
    print('\t#failed images: {}'.format(len(this_lines) - this_total_imgs))
    mother_train += independent_train_count
    mother_val += independent_val_count

print()
print('$$$$$$$$$$$$$$$$B$I$G$$$M$O$N$E$Y$$$$$$$$$$$$$$$$')
print('Mother total train: {}'.format(mother_train))
print('Mother total val: {}'.format(mother_val))

with open(os.path.join(modir,'pp_finetune.train'),'w') as f:
    f.writelines(train_list)

with open(os.path.join(modir,'pp_finetune.val'),'w') as f:
    f.writelines(val_list)

with open(os.path.join(modir,'failed_images.txt'),'w') as f:
    f.writelines(failed_list)

        # lines.extend(this_lines)
    # print('{}: {} images'.format(os.path.basename(fp), len(this_lines)))
# for line in lines:
#     split = line.strip().replace(';','').split()
#     img_path = split[0]
#     assert os.path.exists(img_path)
#     im = Image.open(img_path)
#     iw, ih = im.size
#     bbs = split[1:]
#     #x_min,y_min,x_max,y_max,class_id
#     txt_strs = []
#     for bb in bbs:
#         x_min, y_min, x_max, y_max, class_id = [int(x) for x in bb.split(',')]

#         w = x_max - x_min + 1
#         h = y_max - y_min + 1
#         cx = x_min + w/2 - 1
#         cy = y_min + h/2 - 1
        
#         ncx = cx / iw
#         ncy = cy / ih
#         nw = w / iw
#         nh = h / ih

#         txt_strs.append('{} {} {} {} {}\n'.format(class_id, ncx, ncy, nw, nh))

#     img_basename = os.path.basename(img_path)
#     basename = img_basename.split('.')[0]

#     txt_fp = os.path.join(modir_label, '{}.txt'.format(basename))
#     with open(txt_fp,'w') as f:
#         f.writelines(txt_strs)

#     src = img_path
#     dst = os.path.join(modir_images,img_basename)
#     os.symlink(src,dst)
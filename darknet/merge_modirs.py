import shutil
import argparse
from pathlib import Path
from pprint import pprint
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--out', help='Path to out directory')
parser.add_argument('--datasets', nargs='+', help='list of darknet datasets to be merge', type=str)
parser.add_argument('--symlink', help='if symlink flag given, symlink will be copied to dst instead of original image', action='store_true')
args = parser.parse_args()

datasets_path = []
for dataset in args.datasets:
    p = Path(dataset)
    print('To be merged: ', p.stem)
    datasets_path.append(p) 

out_path = Path(args.out)
print('Merged dataset name: ', out_path.stem)
print('Outputting merged dataset to {}'.format(out_path))

if args.symlink:
    print('Image symlinks will be copied over.')
else:
    print('Original images will be copied over instead of symlink.')

out_img_dir = out_path / 'images'
out_label_dir = out_path / 'labels'
out_img_dir.mkdir(parents=True, exist_ok=True)
out_label_dir.mkdir(parents=True, exist_ok=True)
copied_imgs = []
copied_labels = []

# train_counts = defaultdict(int)
counts = { 'train':  defaultdict(int),
            'val' :  defaultdict(int) }
# val_counts = defaultdict(int)
train_fps = []
val_fps = []
for dp in datasets_path:
    for f in dp.glob('*'):
        if 'part' in f.name:
            if 'train' in f.name:
                with f.open('r') as rf:
                    for l in rf.readlines():
                        train_fps.append(l.strip())
                        counts['train'][dp.stem] += 1
            elif 'val' in f.name:
                with f.open('r') as rf:
                    for l in rf.readlines():
                        val_fps.append(l.strip())
                        counts['val'][dp.stem] += 1
        elif 'images' in f.name and f.is_dir():
            for img in f.glob('*'):
                if img in copied_imgs:
                    raise Exception('Name clash in images! Clash at {}'.format(img))
                dst_file = out_img_dir / img.name
                if not dst_file.is_file():
                    shutil.copy(str(img), str(dst_file), follow_symlinks=(not args.symlink))
                copied_imgs.append(img)
        elif 'labels' in f.name and f.is_dir():
            for lab in f.glob('*'):
                if lab in copied_labels:
                    raise Exception('Name clash in labels! Clash at {}'.format(lab))
                dst_file = out_img_dir / lab.name
                if not dst_file.is_file():
                    shutil.copy(str(lab), str(dst_file), follow_symlinks=(not args.symlink))
                copied_labels.append(lab)

# print('Train partial txts:')
# print(train_fps)
# print('Val partial txts:')
# print(val_fps)
# print('Train image counts')
# pprint(dict(train_counts))
# print('Val image counts')
# pprint(dict(val_counts))
pprint(counts)

# Check for clash in filenames
def get_dupes(l):
    seen = {}
    dupes = []
    for x in l:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dupes.append(x)
            seen[x] += 1
    return dupes
all_image_names = train_fps.copy()
all_image_names.extend(val_fps)
all_image_names_set = set(all_image_names)
if len(all_image_names_set) != len(all_image_names):
    dups = get_dupes(all_image_names)
    print('Name clash for these filenames:', dups)
    raise Exception('Name clash')

## Write out
out_train_part = out_path / 'data.train.part'
with out_train_part.open('w') as f:
    for fp in train_fps:
        f.write('{}\n'.format(fp))

out_val_part = out_path / 'data.val.part'
with out_val_part.open('w') as f:
    for fp in val_fps:
        f.write('{}\n'.format(fp))

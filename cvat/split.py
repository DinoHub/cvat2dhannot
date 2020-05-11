# import sys
import argparse
from tqdm import tqdm
from shutil import copyfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('indir',help='Input directory')
parser.add_argument('--bs', help='Batch size [default: 1000]', type=int, default=1000)
args = parser.parse_args()
# dir_ = sys.argv[1]
dir_ = args.indir
dirpath = Path(dir_)
assert dirpath.is_dir()

# bs = int(sys.argv[2])
bs = int(args.bs)

# out = sys.argv[3]
out_dir_path = Path(str(dirpath)+'_splits-of-{}'.format(bs))
out_dir_path.mkdir(parents=True, exist_ok=True)

img_exts = ['.jpg','.png']
impaths = []
meta_file_path = None
for impath in dirpath.glob('**/*'):
    if str(impath.name).startswith('meta_od_track') and str(impath.name).endswith('.txt'):
        meta_file_path = impath
    elif str(impath).endswith(tuple(img_exts)):
        frame_idx = int(str(impath.stem).split('_')[1])
        impaths.append((str(impath), frame_idx))
if meta_file_path: 
    copyfile(meta_file_path, out_dir_path / meta_file_path.name)
else:
    print('WARNING meta file not found!')

impaths_sorted = sorted(impaths, key=lambda x:x[1])

# each = len(impaths_sorted)//(num_splits-1)
# print('each', each)

# collections = []
for i, k in enumerate(range(0, len(impaths_sorted), bs)):
    # collections.append()
    this_paths = impaths_sorted[k:k+bs]

    subdirname = dirpath.name+'_split_{}'.format(i) 
    subdirpath = out_dir_path / subdirname 

    subdirpath.mkdir(parents=True, exist_ok=True)

    for p in tqdm(this_paths):
        og_path = p[0]
        out_path = subdirpath / Path(og_path).name
        # print(og_path, out_path)
        copyfile(og_path, out_path)

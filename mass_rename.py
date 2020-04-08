import os
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('in_dir')
parser.add_argument('rename',help='Unwanted substring in filename')
parser.add_argument('to', help='String to replace unwanted substring in filename')
args = parser.parse_args()

in_dir = args.in_dir
assert os.path.isdir(in_dir)
# unwanted_string = ':'
unwanted_string = args.rename
assert unwanted_string
# replace_string = '-'
replace_string = args.to
assert replace_string

def rename(root, filename, unwanted, replace):
    newname = filename.replace(unwanted,replace)
    oldpath = os.path.join(root, filename)
    newpath = os.path.join(root, newname)
    # print('Renaming {} to {}'.format(oldpath, newpath))
    os.rename(oldpath, newpath)
    return newpath

def rename_content(root, filename, unwanted, replace):
    filepath = os.path.join(root, filename)
    print('Renaming filepaths in content of {}'.format(filepath))

    write_lines = []
    with open(filepath,'r') as f:
        for line in f.readlines():
            splits = line.strip().split(' ')
            splits[0] = splits[0].replace(unwanted, replace)
            line_string = ' '.join(splits)
            write_lines.append(line_string)
    with open(filepath,'w') as f:
        for line in write_lines:
            f.write('{}\n'.format(line))

print('Renaming colons to dashes..')

indir_basename = os.path.basename(in_dir)
if unwanted_string in indir_basename:
    root_parent = os.path.abspath(os.path.join(in_dir, os.pardir))
    in_dir = rename(root_parent, indir_basename, unwanted_string, replace_string)

for root, dirs, files in tqdm(os.walk(in_dir, topdown=False)):
    for dir_ in dirs:
        if unwanted_string in dir_:
            rename(root, dir_, unwanted_string, replace_string)
    for file in files:
        if file.startswith('meta_od_track_') and file.endswith('.txt'):
            rename_content(root, file, unwanted_string, replace_string)
        if unwanted_string in file:
            rename(root, file, unwanted_string, replace_string)
print('Done!')
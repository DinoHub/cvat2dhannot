import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('data_text', type=str, help='Path to dh annot dataset annot text')
args = parser.parse_args()

data_text_path = Path(args.data_text)
assert data_text_path.is_file()

bb_count = 0
img_count = 0
with data_text_path.open('r') as f:
    for line in f.readlines():
        splits = line.strip().split(' ')
        if splits[0].endswith(('.png','.jpg')):
            img_count += 1
            bb_count += len(splits[1:])

print('{} has {} bbs in {} frames'.format(data_text_path.parent.stem, bb_count, img_count))

import json
import argparse
from pathlib import Path
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('jsonpath')
parser.add_argument('coco_cats') 
parser.add_argument('mappingtxt')
args = parser.parse_args()


with open(args.jsonpath, 'r') as f:
    annots = json.load(f)

with open(args.coco_cats, 'r') as f:
    coco_cats = json.load(f)


mapping = {}
with open(args.mappingtxt, 'r') as f:
    for line in f.readlines():
        bef, aft = line.strip().split(':')
        mapping[int(bef)] = int(aft)

pprint(mapping)

annots['categories'] = coco_cats

for annot in annots['annotations']:
    new_cat = mapping[int(annot['category_id'])]
    annot['category_id'] = new_cat


jsonpath = Path(args.jsonpath)
new_jsonpath = jsonpath.parent / '{}{}{}'.format(jsonpath.stem, '_cococats',jsonpath.suffix)

with new_jsonpath.open('w') as f:
    json.dump(annots, f)
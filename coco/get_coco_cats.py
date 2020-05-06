import json
from pprint import pprint

coco_annot_json = '/media/dh/HDD/coco/coco/annotations/instances_val2014.json'

with open(coco_annot_json,'r') as f:
    annots = json.load(f)


cat_dicts = annots['categories']
pprint(cat_dicts)

with open('coco_cats.json','w') as f:
    json.dump(cat_dicts, f)
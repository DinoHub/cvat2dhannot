import json
import argparse
from tqdm import tqdm
from PIL import Image
from pathlib import Path
from pprint import pprint
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('imagelist', help='list of image paths') 
parser.add_argument('imageroot', help='path to directory containing images')
parser.add_argument('labelroot', help='path to directory containing labels')
parser.add_argument('classnames', help='path to txt with class names')
parser.add_argument('outpath', help='output json path')
args = parser.parse_args()

'''
info{
"year": int, "version": str, "description": str, "contributor": str, "url": str, "date_created": datetime,
}
'''
now = datetime.now()
year = now.year
day = now.strftime('%Y/%m/%d')
info_dict = {
    "year": year,
    "version": '1.0',
    "description": 'DH PP Modir',
    "contributor": "DH",
    "date_created": day
}
# pprint(info_dict)

'''
license{
"id": int, "name": str, "url": str,
}
'''

licenses = [{
    "id": 0,
    "name": 'No License',
    "url": ""
}]
# pprint(licenses)

'''
categories[{
"id": int, "name": str, "supercategory": str,
}]
'''
cat_id_offset = 1
category_dicts = []
with open(args.classnames,'r') as f:
    classes = [l.strip() for l in f.readlines()]
for cat_id, clss in enumerate(classes):
    cat_dict = { 
        'id': cat_id + cat_id_offset,
        'name':clss,
        'supercategory':clss
    }
    category_dicts.append(cat_dict)

pprint(category_dicts)

img_list = None
with open( args.imagelist, 'r' ) as f:
    img_list = [l.strip() for l in f.readlines()]
'''
image{
"id": int, "width": int, "height": int, "file_name": str, "license": int, "flickr_url": str, "coco_url": str, "date_captured": datetime,
}

'''
image_dicts = []
annot_dicts = []
image_id = 0
annot_id = 0
for img_path in tqdm(img_list):
# for img_path in tqdm(img_list[:10]):
    image_dict = {}
    image_dict['id'] = image_id

    width, height = Image.open(img_path).size
    image_dict['width'] = int(width)
    image_dict['height'] = int(height)
    image_dict['file_name'] = Path(img_path).name

    # pprint(image_dict)    
    
    label_path = Path(args.labelroot) / '{}.txt'.format( Path(img_path).stem )
    with label_path.open('r') as lf:
        label_lines = [l.strip() for l in lf.readlines()]
        for lab_line in label_lines:
            toks = lab_line.split()
            class_id = int(toks[0])
            x_rel = float( toks[1] )
            y_rel = float( toks[2] )
            w_rel = float( toks[3] )
            h_rel = float( toks[4] )

            x1_rel = x_rel - w_rel/2. 
            y1_rel = y_rel - h_rel/2.
            # x2_rel = x_rel + w_rel/2. 
            # y2_rel = y_rel + h_rel/2.

            x1_abs = x1_rel * width
            y1_abs = y1_rel * height
            w_abs = w_rel * width
            h_abs = h_rel * height
            area = w_abs * h_abs
            # x2_abs = x2_rel * width
            # y2_abs = y2_rel * height

            '''
            annotation{
                "id": int, "image_id": int, "category_id": int, "segmentation": RLE or [polygon], "area": float, "bbox": [top left x position, top left y position, width, height], "iscrowd": 0 or 1,
            }
            '''

            annot = {
                "id": annot_id,
                "image_id": image_id,
                "category_id": class_id + cat_id_offset,
                "area": area,
                "bbox": [x1_abs, y1_abs, w_abs, h_abs],
                "iscrowd": 0
            }
            annot_id += 1
            annot_dicts.append(annot)
            # pprint(annot)

    image_id += 1
    image_dicts.append(image_dict)

'''
COCO format
{
"info": info, "images": [image], "annotations": [annotation], "categories": categories, "licenses": [license],
}
'''

coco_annot_dict = {
    'info'  : info_dict,
    'images': image_dicts,
    'annotations': annot_dicts,
    'categories': category_dicts,
    'licenses': licenses
}

# pprint(coco_annot_dict)

with open(args.outpath, 'w') as f:
    json.dump(coco_annot_dict, f)
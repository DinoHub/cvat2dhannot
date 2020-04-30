import cv2
import argparse
from tqdm import tqdm
from shutil import copyfile
from pathlib import Path
from keras_yolo3.yolo import YOLO

IMG_EXTS = ['.png','.jpg','.jpeg']
out_img_ext = 'png'

parser = argparse.ArgumentParser()
parser.add_argument(
    "img_dir", help="Directory containing images", type=str
)
parser.add_argument(
    "--thresh", help="Object Detection threshold", type=float, default=0.3
)
parser.add_argument(
    "--buffer", help="Buffer around bounding box in ratio", type=float, default=0.2
)
parser.add_argument(
    "--viz", help='flag to viz results', action='store_true')
args = parser.parse_args()
assert args.thresh > 0.0
assert args.buffer >= 0.0
img_dir_path = Path(args.img_dir)
assert img_dir_path.is_dir()
out_img_dir = args.img_dir+'_yolocropped'
out_img_dir_path = Path(out_img_dir)
out_img_dir_path.mkdir(exist_ok=True, parents=True)

def crop_bbs(frame, res):
    good = []
    # max_conf = -1.0
    # max_bb = None
    crops = []
    for this_res in res:
        bb, conf, cl = this_res
        if cl != 'ship' or conf < args.thresh:
            continue
        l,t,r,b = bb
        crops.append(frame.copy()[t:b, l:r])
    return crops

od = YOLO(
    bgr=True,
    gpu_usage=0.3,
    score=0.05,
    input_image_size=(10,10),
    model_path="keras_yolo3/model_data/pp_reanchored_best_val.h5",
    anchors_path="keras_yolo3/model_data/PP_ALL_anchors.txt",
    classes_path="keras_yolo3/model_data/PP_classes.txt",
)
print('YOLO inited.')

# exporter = CVAT_exporter(upload_format='yolo', out_dir=str(img_dir_path)+'_preds')

full_img_count = 0
crops_count = 0
no_cropped_count = 0

# for impath in img_dir_path.glob('**/*'):
for impath in tqdm(list(img_dir_path.glob('**/*'))):
    if not str(impath).endswith(tuple(IMG_EXTS)):
        continue
    img = cv2.imread(str(impath))

    od.input_image_size=img.shape[:2]
    
    res = od.detect_get_box_in(
        img,
        box_format="ltrb",
        classes=["ship"],
        buffer_ratio=args.buffer,
    )

    crops = crop_bbs(img.copy(), res)

    if args.viz:
        show_frame = img.copy()
        for this_res in res:
            bb, conf, cl = this_res
            l,t,r,b = bb
            cv2.rectangle(show_frame, (l,t), (r,b), color=(255,255,0), thickness=2)
        cv2.imshow(impath.name,show_frame)
        for i, cropped in enumerate(crops):
            cv2.imshow(impath.name+' cropped {}'.format(i), cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    full_img_count += 1
    if len(crops) > 0:
        for i, crop in enumerate(crops):
            crops_count += 1
            crop_path = out_img_dir_path/'{}_cropped_{}.{}'.format(impath.stem, i+1, out_img_ext)
            cv2.imwrite(str(crop_path), crop)
    else:
        no_cropped_count += 1
        out_file = out_img_dir_path/'{}_full.{}'.format(impath.stem, out_img_ext)
        copyfile(str(out_img_dir_path), out_file)

print('Cropped @ {} confidence threshold and buffer ratio of {}'.format(args.thresh, args.buffer))
print('Total full frames: {}'.format(full_img_count))
print('\\__No crop: {}'.format(no_cropped_count))
print('\\__Cropped: {}'.format(full_img_count - no_cropped_count))
print('\t\\__total crops: {}'.format(crops_count))
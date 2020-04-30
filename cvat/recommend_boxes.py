import cv2
import argparse
from tqdm import tqdm
from pathlib import Path
from keras_yolo3.yolo import YOLO
from cvat_exporter import YOLO_exporter

IMG_EXTS = ['.png','.jpg','.jpeg']

parser = argparse.ArgumentParser()
parser.add_argument(
    "img_dir", help="Directory containing images", type=str
)
parser.add_argument(
    "--thresh", help="Object Detection threshold", type=float, default=0.1
)
parser.add_argument(
    "--viz", help='flag to viz results', action='store_true')
args = parser.parse_args()
assert args.thresh > 0.0
img_dir_path = Path(args.img_dir)
assert img_dir_path.is_dir()

def get_good_bbs(res):
    good = []
    for this_res in res:
        bb, conf, cl = this_res
        l,t,r,b = bb
        if cl == 'ship' and conf > args.thresh:
            good.append(this_res)
    return good

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

exporter = YOLO_exporter(out_dir=str(img_dir_path)+'_preds')

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
        buffer_ratio=0.0,
    )

    good_res = get_good_bbs(res)
    exporter.write(impath, good_res)

    if args.viz:
        show_frame = img.copy()
        for this_res in good_res:
            bb, conf, cl = this_res
            l,t,r,b = bb
            cv2.rectangle(show_frame, (l,t), (r,b), color=(255,255,0), thickness=2)
        cv2.imshow(impath.name,show_frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

exporter.end()
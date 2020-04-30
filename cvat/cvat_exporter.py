import shutil
from PIL import Image
from pathlib import Path

class YOLO_exporter(object):
    def __init__(self, out_dir=None):
        self.out_dir_path = Path(out_dir) 
        self.out_dir_path.mkdir(exist_ok=True, parents=True)
        self.classes = []
        self.imnames = []
        self.cvat_arbitary_dir_name = 'obj_train_data'
        (self.out_dir_path/self.cvat_arbitary_dir_name).mkdir(exist_ok=True, parents=True) 

    def write(self, impath, preds):
        im = Image.open(impath)
        iw, ih = im.size

        impath = Path(impath)
        # txt_fp = Path(str(impath).replace(impath.suffix, '.txt'))
        txt_fp = self.out_dir_path / self.cvat_arbitary_dir_name / impath.name.replace(impath.suffix,'.txt')
        # print('Writing {}'.format(txt_fp.name))
        self.imnames.append(impath.name)
        with open(txt_fp, 'w') as f:
            for pred in preds:
                bb, _, cl = pred
                if cl not in self.classes:
                    self.classes.append(cl)
                class_idx = self.classes.index(cl)
                l,t,r,b = bb
                
                w = r - l + 1
                h = b - t + 1
                cen_x = l + (r - l)/2
                cen_y = t + (b - t)/2
                
                cen_x = cen_x / iw
                cen_y = cen_y / ih
                w = w/iw
                h = h/ih

                write_str = '{} {} {} {} {}\n'.format(class_idx, cen_x, cen_y, w, h)
                f.write(write_str)
                # print(write_str)

    def end(self):
        with (self.out_dir_path/'obj.data').open(mode='w') as f:
            f.write('classes = {}\n'.format(len(self.classes)))
            f.write('train = data/train.txt\n')
            f.write('names = data/obj.names\n')
            f.write('backup = backup/\n')
        
        with (self.out_dir_path/'obj.names').open(mode='w') as f:
            for cl in self.classes:
                f.write(cl+'\n')

        with (self.out_dir_path/'train.txt').open(mode='w') as f:
            for imname in self.imnames:
                fake_path = Path('data') / self.cvat_arbitary_dir_name / imname  
                f.write(str(fake_path)+'\n')

        print('Zipping up..')
        shutil.make_archive(str(self.out_dir_path),'zip',str(self.out_dir_path))

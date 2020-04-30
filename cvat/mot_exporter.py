
class MOT_exporter(object):
    def __init__(self, out_file=None):
        self.out_file_path = Path(out_file) 
        self.imgname2bbs = defaultdict(list)

    def write_preds(self, frame_idx, preds):
        '''
        The MOT CSV format
        Frame number (starts from 0), Track id (starts from 0), l, t, w, h, Confidence, Class (in string),Visibility ratio (how much of the object is visible, default is 1.0)
        '''
        
        with self.out_file_path.open(mode='w') as f:

            for pred in preds:
                assert len(pred) == 4
                bb, conf, cl, track_id = pred
                # if cl not in self.classes:
                    # self.classes.append(cl)
                # class_idx = self.classes.index(cl)
                l,t,r,b = bb
                
                w = r - l + 1
                h = b - t + 1

                write_str = '{},{},{},{},{},{},{},{},{}\n'.format(frame_idx, track_id, l,t,w,h, conf, cl, 1.0 )
                f.write(write_str)
                print(write_str)

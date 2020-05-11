import os
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
parser.add_argument('--roots', nargs='+', help='list of paths to roots')
args = parser.parse_args()

ds = []
for root in args.roots:
    for d in Path(root).glob('*'):
        if d.is_dir():
            ds.append(d)

for f in Path(args.input).rglob('*'):
    try:
        link = os.readlink(f)
    except OSError:
        continue

    link_path = Path(link)
    curr_dir = f.parent
    link_parts = link_path.parts
    for root in ds:
        if root.name in link_parts:
            idx = link_parts.index(root.name)
            partpath = Path(*link_parts[idx+1:])
            new_abs_path = Path(root) / partpath
            assert new_abs_path.is_file(),'{}'.format(new_abs_path)
            new_rel_path = os.path.relpath(new_abs_path, curr_dir)
            f.unlink()
            f.symlink_to(new_rel_path)
            assert f.is_symlink(),'{}'.format(f)
            print(new_rel_path)
            break
    else:
        print('NONE', link)
        raise Exception('Cannot find dir in root given.')
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('inp', help='Path to txt file to generate part')
args = parser.parse_args()

in_path = Path(args.inp)

with in_path.open('r') as f:
    lines = f.readlines()

out_path = in_path.parent / '{}{}'.format(in_path.name,'.part')

with out_path.open('w') as wf:
    for line in lines:
        part_path = line.strip().split('images/')[-1]
        wf.write('images/{}\n'.format(part_path))

print('Output at ', out_path)

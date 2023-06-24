import argparse
parser = argparse.ArgumentParser(prog='recurrink')
parser.add_argument("-c", "--control",  default=0, help="Control 0-9 zero is random")
args = parser.parse_args()

a = [
  ['a', 'b', 'c', 'd'],
  ['e', 'f', 'g', 'h'],
  ['i', 'j', 'k', 'l'],
  ['m', 'n', 'o', 'p']
]
c = int(args.control)
[print(a[c][x], ' ', end='') for x in range(0, 4)]
print()

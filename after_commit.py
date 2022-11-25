#!/usr/bin/python3
# after_commit.sh
# prepares the next commit by incrementing the version numbers.
# It is possible to increment the patch, minor or major level.
# The reference version number is in python/__init__.py.
# In all files of the "Targets" list, the version number
# after the pattern "Version=" will be replaced by the updated version string.
# A version number is detected by the re "[0-9\.]*"

import re
import argparse


Targets = ["README.md"]
Source = "python/__init__.py"
exp = re.compile('Version=[^"]*"([0-9\.]*)"')
Version = None
NewVersion = None

def update(fn):
    tgf = ""
    with open(fn, encoding="utf-8") as dst:
        while ln := dst.readline():
            mat = exp.search(ln)
            if mat:
                ln = ln[:mat.start(1)] + NewVersion + ln[mat.end(1):]
            tgf += ln
    with open(fn, "wt") as dst:
        dst.write(tgf)
        
parser = argparse.ArgumentParser(prog='after_commit.py')
parser.add_argument('which', nargs='?', choices=['major','minor','patch'], default='patch')

with open(Source, encoding="utf-8") as src:
    while ln := src.readline():
        mat = exp.search(ln)
        if mat:
            Version = mat.group(1)
            break

if Version == None:
    print("Reference not found")
    sys.exit(1)

vernums = Version.split('.')
if len(vernums) != 3:
    print("malformed reference version {}".format(Version))
    sys.exit(1)
    
args = parser.parse_args()
if args.which == 'major':
    vernums[0] = str(int(vernums[0])+1)
    vernums[1] = '0'
    vernums[2] = '0'
elif args.which == 'minor':
    vernums[1] = str(int(vernums[1])+1)
    vernums[2] = '0'
else:
    vernums[2] = str(int(vernums[2])+1)
NewVersion = vernums[0] + '.' + vernums[1] + '.' + vernums[2]

update(Source)

for fn in Targets:
    update(fn)

The current file structure 

'''
models
├── afroclave.csv
├── afroclave.json
├── afroclave.rink
├── arpeggio.csv
├── arpeggio.json
├── arpeggio.rink
'''

The target

models 
+------ # csv file to define layout of cells
+------ # json source file for cell attributes
+------ # interim file for inkscape conversion

pub
+-- arpeggio        # model name
+------ c152bcd1dee8915e90dfe28c05bf3774.json # model instance generated from source as json
+------ c152bcd1dee8915e90dfe28c05bf3774.svg  # model instance generated from source as svg
+------ c152bcd1dee8915e90dfe28c05bf3774.png # publish format for instagram

pub.log
date,model,model_id

## model naming
original idea was to rename based on x-y-numofcells. For example a 2 x 2 matrix with 3 cells would be
02 02 03
but numeric names clash!

60 04 05 sexagesimal
24 18 14 afroclave
06 02 06 buleria
12 12 07 eflat
12 06 04 waltz
06 06 09 pitch
04 06 24 bossa
12 12 05 mambo
03 02 04 soleares
06 06 12 fourfour
06 06 06 arpeggio
06 06 06 tumbao

so insead the task is to make ./recurrink.py -l output the above

## integrate mondrian.sh with recurrink, input and effect python

- mondrian randomly selects model and obtains a cell list
./recurrink.py -m soleares --cells  
# recurrink generates all values in /tmp/soleares.CSV
< a b c d
- for each cell get values
./recurrink.py -m soleares --cells a 
# recurrink look-up in tmp
< 1,square,north
- mondrian updates /tmp/soleares.SVG using effect.py
- after loop: mondrian asks recurrink to clean-up
./recurrink.py -m soleares --save      
# recurrink reads CSV and creates digest then writes JSON and returns
< a6cf936f6da2b1706f792da
- mondrian moves SVG and deletes tmp CSV







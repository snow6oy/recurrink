# Block

A Block is a collection of cells. The block module provides operations on the collection.

## Palette

- restore GPL files from DB for pals 8..11 
- add stabilo fine
- stroke has ##
- single-source-of-truth for palettes, see config.py in model/README
- migrate universal PIDs to new palettes until 60
- the problem of univsersal palette: solve by ranges color > r1 and < r2
- Stencil broke recurrink commit because it counted colours
- review doc/ddl-palett2.sql decide if benefits matches impact of schema change

## Meander

- padding can be exposed to the interface, as meta in the conf?
- meander: concentric could work for circles, triangles and diamonds
- resurrect the original meander and apply N or E in conf 
- add meander.style as a YAML attribute


## Pen names

> as a plotter controller i want to see a  
> display of pen names in inkscape   
> so that i know which pen to load next  


Create a GPL file.
stabilo68.gpl example

```
Library/Application Support/org.inkscape.Inkscape/config/inkscape/palettes/

r   g   b      penam hex
---------------------------
128 255 179 #  13    80ffb3
```
generate a palette text file with permutations of fg:op:bg

```
./recurrink init -p GPLFILE

palettes/stabilo68.txt
```
The palette file is a tab-seperated list
```
fill    opacity background
#d7e3f4 0.5     #483737
```
The hex in the GPL and ver will become a composite PRIMARY KEY in the pens table.

```
./recurrink commit --inkpal GPLFILE
```
Now palettes/GPLFILE is in sync with db.pens. Optionally add the new pens to the palette table.

```
./recurrink commit -p12
11 new colours 
66 new entries
```
To see the pen names in Inkscape explode has to pass them to the SVG.

3. Block.styles recieves pen names from db
4. Model.linear replaces group id with penam OR fallback to fill name


-------------------------------------------------------------------------------
### Palette validation
> as a rink designer i want  
> to improve colour validation  
> with a simpler method of applying colour

relax validation so that at build time
fg:bg:op are checked individually, not as a trio
warn when opacity is a value other than (None,1,0.5)

checks are done against pens table, colours can be dropped
the method of generating a pallete with math.comb can be archived
the HTML palette pages show each colour exactly once (not trios)

cells table still refers to pid:sid
at commit time, missing palette entries should be added 
palette entries are no longer tied to ver
but they must honour existing pids. pid=fg:bg:op

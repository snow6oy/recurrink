# TODO
COMMAND
move biz logic in recurrink as already done for init

    build               build svg from config
    explode             stamp blocks on the grid
    clone               get copy of config
    init                generate config
    commit              write immutable entry to db
      -publish             add release date to db
      -delete              remove rink from db
    x compare             compare palettes
    info
      -ls                  list models or palettes
      -read                get rink metadata

reduce commands to 6
push 4 to be new sub-commands
remove 1

CLONE
model/clone merge of recurrink.clone model.palette block.palette 
block/clone BlockClone called by MpdelClone to access BlockData
cell/layers cell/transform called directly by BlockClone

VALIDATION
stroke value is determined by rink.ver and must correspond with colors.ver

DASHARRAY
dash spacing should relate to the pen.
Define dash space as a multiple of pen width. 
e.g. pen width is 0.4 and dash is two
then dash has length:0.8 and gap:0.8

DATA CONVERSION
convert internal object to svg structure JUST IN TIME creating shapely

BUILD ALL
can output MODEL/PEN_1..n
and        PEN/MODEL_1..n

when run as build -a pen|model|None

# DONE
DATABASE
stroke width is an attribute of pen
  widthmm DECIMAL,

DATA IMPORT
import from db1 with hex values assigned to VER:0
defer assignment to new pal until rink is elected for re-use

 2239  ./palswap clone -d5bd0d8405d453b47f0ba8359b71d750e -o
 2240  ./palswap commit -m testcard -x -odb2

DATA ACCESS
after inserting new records each access class can update .count with
new record count, .e.g md2.model(name=flute) print(md2.count, updated)

geom + colors + strokes = layers
stroke and dasharray are the only style attributes useful for plotters

LAYERS Table
 rinkid
 cell
 layer
 name
 size
 facing 
 stroke
 dasharray

top (and metadata) are immutable during build. YAML edits are ignored.

EXAMPLE A
when top is False

stroke: [null, ff0000]
  dash: [null, 1]

result: empty background with a dashed red line on foreground shape

EXAMPLE B
when top is True

stroke: [00ff00]

result: a solid green line on top of allocated cell

EXANPLE C
Neither stroke or dash are defined and top is either true or false

geom: { name ... }

result: empty background with a solid black line

PREVIEW
Caveats of reducing style attributes to stroke and dash.
1. During preview build, color is displayed with fill. 
The fill value is borrowed from stroke and so a border line cannot be shown

2. In the final build for plotting, fill is always none. 
A zigzag line cannot be filled because a pen only understands linear


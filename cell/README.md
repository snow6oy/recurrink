# Cell

The Cell module uses Shapely to implement the geometrical properties of a rink.

A Cell is always a MultiPolygon and can contain up to three Polygons.

1. Background
1. Foreground
1. Top (optional)

## TODO

- background: None in YAML should remove Polygon from layer 0
- raise warning when background is present and top:True
- CLEN + POS = Shapely.bounds. Need this for Sesanta e.g. cell.bounds = (0,0,5,12)
- move data.py to block/* because data access pattern is not by cell
- size can use Shapely.buffer and facing transform,e.g E == 90 degrees
- Extend facing so small shapes can be placed in any of 9 cubes 
  `N E S W NE SW NW SE C`

## Refactor Layer
Shapely supports z dimension. Why not use to implement bft ?
```
bg  = Polygon(  (0,0),   (9,0) ..
fg  = Polygon((0,0,0), (9,0,0) ..
top = Polygon((0,0,0), (9,0,1) ..
bg.has_z > False
fg.has_z > True
```

Archive

cell/cellmaker.py
cell/geomink.py
cell/meander.py
cell/shape.py
cell/shapes.py

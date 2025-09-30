# Cell

The Cell module uses Shapely to implement the geometrical properties of a rink.

A Cell is always a MultiPolygon and can contain up to three Polygons.

1. Background
1. Foreground
1. Top (optional)

## Runbook

> as a plotter using white paper i want to ignore some  backgrounds

`background: null`  in YAML will cause it to be ignored

### Design

- raise warning when background is present and top:True
- CLEN + POS = Shapely.bounds. Need this for Sesanta e.g. cell.bounds = (0,0,5,12)
- move data.py to block/* because data access pattern is not by cell
- size can use Shapely.buffer and facing transform,e.g E == 90 degrees
- Extend facing so small shapes can be placed in any of 9 cubes 
  `N E S W NE SW NW SE C`

## Refactor Layer

> as a code maintainer i want a consistent way to navigate a Cell

Shapely supports z dimension. Why not use to implement bft ?
```
bg  = Polygon(  (0,0),   (9,0) ..
fg  = Polygon((0,0,0), (9,0,0) ..
top = Polygon((0,0,0), (9,0,1) ..
bg.has_z > False
fg.has_z > True
```


> as a plotter i want diamonds and circles to be linear


9. Move makeDiagonals to cell.shape.Diamond
10. Add Circle
1. Move Rectangular Meander with composites
1. Rename coords/meander paint/draw
11. Layer should make either polygn OR polyln

DONE  
1. Temporary scaffolding in Layer for Triangle
4. Draw a triangle using recurrink
1. Inherit Shape from Triangle
6. Move/copy Meander to cell as Shape

DONE WITH IMPLICATIONS
- Shape.guideline will need to substitute polygon.bounds with clen
- Gnomon surface test will need another solution

WONT DO.
- Temporary scaffolding in Make for Triangle
- Fix bug with half.sized triangles North and South


Also consider That if points + dimension only make Blocks
then why process XY as Shapely.transform does it too  ?

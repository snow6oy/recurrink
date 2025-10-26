# Cell

The Cell module uses Shapely to implement the geometrical properties of a rink.

In Paint mode a Cell is a MultiPolygon that contains up to three Polygons.

1. Background
1. Foreground
1. Top (optional)

A cell is a LineString when in Draw mode.

## Runbook

> as a plotter using white paper i want to ignore some  backgrounds

`background: null`  in YAML will cause it to be ignored


> as a designer i want no more than two layers because more is muddy

- when background is present and top:True then ignore background 
  and validate bft <= 2 in length

## Design

- CLEN + POS = Shapely.bounds. Need this for Sesanta e.g. cell.bounds = (0,0,5,12)
- move data.py to block/* because data access pattern is not by cell
- size can use Shapely.buffer and facing transform,e.g E == 90 degrees
- Extend facing so small shapes can be placed in any of 9 cubes 
  `N E S W NE SW NW SE C`

### Refactor top as Shapely z

> as a code maintainer i want a consistent way to navigate a Cell

Shapely supports z dimension. Why not use to implement bft ?
```
bg  = Polygon(  (0,0),   (9,0) ..
fg  = Polygon((0,0,0), (9,0,0) ..
top = Polygon((0,0,0), (9,0,1) ..
bg.has_z > False
fg.has_z > True
```

### Add all shapes to Linear

> as a plotter i want diamonds and circles to be linear

1.  fix large circles t.circle.Test.test_e
1.  triangles became inverted in Linear:True
1.  Square Rings 
1.  remove Rectangle(edge) if unused


## Release notes

### 2025-10-19

1. Layer makes either polygn OR polyln
1. Triangle and Diamond guidelines override meander
1. Coords is a private method for paint/draw
1. Added spiral as Rectangle(name) test with recurrink
1. Added Circle to meander
1. Temporary scaffolding in Layer for Triangle
4. Drew a triangle using meander
6. Moved Meander to cell
1. Fixed bug with half.sized triangles North and South

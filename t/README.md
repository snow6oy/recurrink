``` 
cd ~/code/recurrink
source v/bin/activate
screen -S rink
python -m unittest t.Test.test_n
```

# Order of Execution
Not numeric after all *face palm*
```
t.layout.Test.test_1
t.layout.Test.test_10
t.layout.Test.test_11
t.layout.Test.test_12
t.layout.Test.test_13
t.layout.Test.test_14
t.layout.Test.test_15
t.layout.Test.test_16
t.layout.Test.test_2
t.layout.Test.test_3
```

# Test Coverage

## Cell

14 cellMaker
 0 geometry
 2 strokes
 0 cellData
 0 plotter
10 meander
 0 points
 5 shape
 0 shapeTriangl
 0 shapeDiamond
 0 shapeCircle
 3 shapeRectangle
 0 shapeVoid
12 shapeParabola
 0 shapeSquareRing

## Model

 5 modelData
 0 db
16 layout
 0 grid
 9 svg
 5 linearSvg

## Block

 0 views
 2 compass
 7 blockData
21 flatten
 7 geoMaker
12 paletteMaker
 8 tmpFile

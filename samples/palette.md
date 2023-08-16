## rink palette
### Implementation plan

- Emulate mirror.py by initialising models already mirrored and adding colour symmetry
- Convert palette.py into an in-memory lookup table. E.g model.reverse(fg) -> bg
- Limit the number of colour per model
- Use the 'all' cells to define the primary palette, and pair 'one' cells with complimentary colours
### Foreground colours
- `#DC143C` crimson
- `#C71585` mediumvioletred
- `#FFA500` orange
- `#32CD32` limegreen
- `#4B0082` indigo
### Background colours
- `#FFF` white
- `#9ACD32` yellowgreen
- `#CD5C5C` indianred
- `#000` black
### Opacity
Opacity can be set at 
* 1.0
* 0.7 
* 0.4 
* 0.0 
### Transparencies
A transparency is when a foreground colour is overlaid onto a background with enough opacity to create a new distinct colour. This gives eight possibilities for each forground.

| white | yellowgreen | indianred | black |
| ---   | ---   | ---       | ---         |
| 0.7   | 0.7   | 0.7       | 0.7         |
| 0.4   | 0.4   | 0.4       | 0.4         |

An overlay is when the foreground and background occupy the same co-ordinates. In most cases, e.g. a triangle there is both an overlay and direct exposure of the background colour. The background colour is opaque (opacity = 1.0). These four colours are not shown below.

The opposite is also a special case. When the foreground is opaque, then the background is hidden. These colours are shown in the first column below.



![](palette.svg)

### Colour table
```
01 02 03 04 05 06 07 08 09 
10 11 12 13 14 15 16 17 18 
19 20 21 22 23 24 25 26 27 
28 29 30 31 32 33 34 35 36 
37 38 39 40 41 42 43 44 45 
```

1. C71585 1.0 000
2. C71585 0.7 FFF
3. C71585 0.7 9ACD32
4. C71585 0.7 CD5C5C
5. C71585 0.7 000
6. C71585 0.4 FFF
7. C71585 0.4 9ACD32
8. C71585 0.4 CD5C5C
9. C71585 0.4 000
10. DC143C 1.0 000
11. DC143C 0.7 FFF
12. DC143C 0.7 9ACD32
13. DC143C 0.7 CD5C5C
14. DC143C 0.7 000
15. DC143C 0.4 FFF
16. DC143C 0.4 9ACD32
17. DC143C 0.4 CD5C5C
18. DC143C 0.4 000
19. FFA500 1.0 000
20. FFA500 0.7 FFF
21. FFA500 0.7 9ACD32
22. FFA500 0.7 CD5C5C
23. FFA500 0.7 000
24. FFA500 0.4 FFF
25. FFA500 0.4 9ACD32
26. FFA500 0.4 CD5C5C
27. FFA500 0.4 000
28. 32CD32 1.0 000
29. 32CD32 0.7 FFF
30. 32CD32 0.7 9ACD32
31. 32CD32 0.7 CD5C5C
32. 32CD32 0.7 000
33. 32CD32 0.4 FFF
34. 32CD32 0.4 9ACD32
35. 32CD32 0.4 CD5C5C
36. 32CD32 0.4 000
37. 4B0082 1.0 000
38. 4B0082 0.7 FFF
39. 4B0082 0.7 9ACD32
40. 4B0082 0.7 CD5C5C
41. 4B0082 0.7 000
42. 4B0082 0.4 FFF
43. 4B0082 0.4 9ACD32
44. 4B0082 0.4 CD5C5C
45. 4B0082 0.4 000


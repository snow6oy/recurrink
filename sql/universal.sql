SELECT DISTINCT(stroke, stroke_width, stroke_dasharray, stroke_opacity) 
FROM styles 
WHERE stroke_width > 0;

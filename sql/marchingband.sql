-- marchingband
-- 2 way parallel, cell symmetry without sexagesimal
INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('marchingband', 6, '{3, 3}', 1.0);
-- a b c d: facing n s e w
-- e f: facing all
-- f a f
-- b e c
-- f d f
INSERT INTO blocks (model, position, cell, top) 
VALUES 
  ('marchingband', '{ 0, 0 }', 'f', 'g'),
  ('marchingband', '{ 1, 0 }', 'a', null),
  ('marchingband', '{ 2, 0 }', 'f', 'g'),
  ('marchingband', '{ 0, 1 }', 'b', null),
  ('marchingband', '{ 1, 1 }', 'e', 'h'),
  ('marchingband', '{ 2, 1 }', 'c', null),
  ('marchingband', '{ 0, 2 }', 'f', 'g'),
  ('marchingband', '{ 1, 2 }', 'd', null),
  ('marchingband', '{ 2, 2 }', 'f', 'g');

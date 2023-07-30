-- timpani
-- 2 way diagonal, cell symmetry without sexagesimal
-- a - l: facing n s e w
-- m: facing all

-- c a b c
-- a b a b
-- b a b a
-- c b a c

-- * / \ *
-- / \ / \
-- \ / \ /
-- * \ / *


INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('timpani', 3, '{4, 4}', 1.0);

INSERT INTO blocks (model, position, cell, top) 
VALUES 
  ('timpani', '{ 0, 0 }', 'c', null),
  ('timpani', '{ 1, 0 }', 'a', 'd'),
  ('timpani', '{ 2, 0 }', 'b', 'e'),
  ('timpani', '{ 3, 0 }', 'c', null),
  ('timpani', '{ 0, 1 }', 'a', 'd'),
  ('timpani', '{ 1, 1 }', 'b', 'e'),
  ('timpani', '{ 2, 1 }', 'a', 'd'),
  ('timpani', '{ 3, 1 }', 'b', 'e'),
  ('timpani', '{ 0, 2 }', 'b', 'e'),
  ('timpani', '{ 1, 2 }', 'a', 'd'),
  ('timpani', '{ 2, 2 }', 'b', 'e'),
  ('timpani', '{ 3, 2 }', 'a', 'd'),
  ('timpani', '{ 0, 3 }', 'c', null),
  ('timpani', '{ 1, 3 }', 'b', 'e'),
  ('timpani', '{ 2, 3 }', 'a', 'd'),
  ('timpani', '{ 3, 3 }', 'c', null);

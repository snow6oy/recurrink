-- timpani
-- 1 way diagonal, cell symmetry without sexagesimal
-- a - d: facing n s e w 	g - k: superimposed	e - f: facing all
INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('timpani', 11, '{4, 4}', 1.0);
-- * / \ *
-- / \ / \
-- \ / \ /
-- * \ / *

-- f a c f 	. g i .
-- a c e d 	g i k j
-- c e d b 	i k j h
-- f d b f 	. j h .

INSERT INTO blocks (model, position, cell, top) 
VALUES 
  ('timpani', '{ 0, 0 }', 'f', null),
  ('timpani', '{ 1, 0 }', 'a', 'g'),
  ('timpani', '{ 2, 0 }', 'c', 'i'),
  ('timpani', '{ 3, 0 }', 'f', null),
  ('timpani', '{ 0, 1 }', 'a', 'g'),
  ('timpani', '{ 1, 1 }', 'c', 'i'),
  ('timpani', '{ 2, 1 }', 'e', 'k'),
  ('timpani', '{ 3, 1 }', 'd', 'j'),
  ('timpani', '{ 0, 2 }', 'c', 'i'),
  ('timpani', '{ 1, 2 }', 'e', 'k'),
  ('timpani', '{ 2, 2 }', 'd', 'j'),
  ('timpani', '{ 3, 2 }', 'b', 'h'),
  ('timpani', '{ 0, 3 }', 'f', null),
  ('timpani', '{ 1, 3 }', 'd', 'j'),
  ('timpani', '{ 2, 3 }', 'b', 'h'),
  ('timpani', '{ 3, 3 }', 'f', null);

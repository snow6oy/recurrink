-- syncopated
-- sexagesimal is divisibility by sixty
-- a - h: facing n s e w
-- i facing: all

INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('syncopated', 10, '{12, 4}', 1.0);

-- x x o x x \ / x x o x x
-- x o x + x / \ x + x o x
-- x o x + x \ / x + x o x
-- x x o x x / \ x x o x x

INSERT INTO blocks (model, position, cell, top) 
VALUES 
  ('syncopated', '{  0, 0 }', 'i', 'j'),
  ('syncopated', '{  1, 0 }', 'i', 'j'),
  ('syncopated', '{  2, 0 }', 'h', null),
  ('syncopated', '{  3, 0 }', 'i', 'j'),
  ('syncopated', '{  4, 0 }', 'i', 'j'),
  ('syncopated', '{  5, 0 }', 'a', null),
  ('syncopated', '{  6, 0 }', 'b', null),
  ('syncopated', '{  7, 0 }', 'i', 'j'),
  ('syncopated', '{  8, 0 }', 'i', 'j'),
  ('syncopated', '{  9, 0 }', 'g', null),
  ('syncopated', '{ 10, 0 }', 'i', 'j'),
  ('syncopated', '{ 11, 0 }', 'i', 'j'),
  ('syncopated', '{  0, 1 }', 'i', 'j'),
  ('syncopated', '{  1, 1 }', 'g', null),
  ('syncopated', '{  2, 1 }', 'i', 'j'),
  ('syncopated', '{  3, 1 }', 'e', null),
  ('syncopated', '{  4, 1 }', 'i', 'j'),
  ('syncopated', '{  5, 1 }', 'c', null),
  ('syncopated', '{  6, 1 }', 'd', null),
  ('syncopated', '{  7, 1 }', 'i', 'j'),
  ('syncopated', '{  8, 1 }', 'f', null),
  ('syncopated', '{  9, 1 }', 'i', 'j'),
  ('syncopated', '{ 10, 1 }', 'h', null),
  ('syncopated', '{ 11, 1 }', 'i', 'j'),
  ('syncopated', '{  0, 2 }', 'i', 'j'),
  ('syncopated', '{  1, 2 }', 'h', null),
  ('syncopated', '{  2, 2 }', 'i', 'j'),
  ('syncopated', '{  3, 2 }', 'f', null),
  ('syncopated', '{  4, 2 }', 'i', 'j'),
  ('syncopated', '{  5, 2 }', 'a', null),
  ('syncopated', '{  6, 2 }', 'b', null),
  ('syncopated', '{  7, 2 }', 'i', 'j'),
  ('syncopated', '{  8, 2 }', 'e', null),
  ('syncopated', '{  9, 2 }', 'i', 'j'),
  ('syncopated', '{ 10, 2 }', 'g', null),
  ('syncopated', '{ 11, 2 }', 'i', 'j'),
  ('syncopated', '{  0, 3 }', 'i', 'j'),
  ('syncopated', '{  1, 3 }', 'i', 'j'),
  ('syncopated', '{  2, 3 }', 'g', null),
  ('syncopated', '{  3, 3 }', 'i', 'j'),
  ('syncopated', '{  4, 3 }', 'i', 'j'),
  ('syncopated', '{  5, 3 }', 'c', null),
  ('syncopated', '{  6, 3 }', 'd', null),
  ('syncopated', '{  7, 3 }', 'i', 'j'),
  ('syncopated', '{  8, 3 }', 'i', 'j'),
  ('syncopated', '{  9, 3 }', 'h', null),
  ('syncopated', '{ 10, 3 }', 'i', 'j'),
  ('syncopated', '{ 11, 3 }', 'i', 'j');
-- i i h i i a b i i g i i
-- i g i e i c d i f i h i
-- i h i f i a b i e i g i
-- i i g i i c d i i h i i

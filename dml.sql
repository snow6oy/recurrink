-- test data
-- validate new schemas here
INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES 
  ('soleares', 4, '{3, 2}', 1.0),
  ('koto', 7, '{6, 2}', 0.75);

INSERT INTO blocks (model, position, cell) 
VALUES 
  ('soleares', '{ 0, 0 }', 'a'),
  ('soleares', '{ 1, 0 }', 'b'),
  ('soleares', '{ 2, 0 }', 'a'),
  ('soleares', '{ 0, 1 }', 'c'),
  ('soleares', '{ 1, 1 }', 'd'),
  ('soleares', '{ 2, 1 }', 'c'),
  ('koto', '{ 0, 0 }', 'a'),
  ('koto', '{ 1, 0 }', 'b'),
  ('koto', '{ 2, 0 }', 'f'),
  ('koto', '{ 3, 0 }', 'e'),
  ('koto', '{ 4, 0 }', 'g'),
  ('koto', '{ 5, 0 }', 'g'),
  ('koto', '{ 0, 1 }', 'c'),
  ('koto', '{ 1, 1 }', 'd'),
  ('koto', '{ 2, 1 }', 'e'),
  ('koto', '{ 3, 1 }', 'f'),
  ('koto', '{ 4, 1 }', 'g'),
  ('koto', '{ 5, 1 }', 'g');

INSERT INTO geometry (shape, size, facing, top) 
VALUES 
  ('triangle', 'medium', 'south', FALSE),
  ('square', 'large', 'south', TRUE),
  ('line', 'large', 'east', TRUE),
  ('square', 'medium', 'north', FALSE);

INSERT INTO styles (fill, bg, fill_opacity, stroke, stroke_width, stroke_dasharray, stroke_opacity)
VALUES
  ('#FFF', '#DC143C', '1.0', '#000', 2, 0, '1.0'),
  ('#FFF', '#000', '1.0', '#000', 6, 0, '1.0'),
  ('#FFF', '#9ACD32', '1.0', '#000', 1, 0, '1.0');
-- use defaults
INSERT INTO styles (sid, fill, bg)
VALUES
  (DEFAULT, '#FFF', '#CCC');

INSERT INTO views (view, model, author, cell, sid, gid) 
VALUES 
  ('e4681aa9b7aef66efc6290f320b43e55', 'soleares', 'machine', 'a', 1, 1),
  ('e4681aa9b7aef66efc6290f320b43e55', 'soleares', 'machine', 'b', 2, 2),
  ('e4681aa9b7aef66efc6290f320b43e55', 'soleares', 'machine', 'c', 3, 3),
  ('e4681aa9b7aef66efc6290f320b43e55', 'soleares', 'machine', 'd', 4, 4);

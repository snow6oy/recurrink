-- test data
-- validate new schemas here
INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('spiral', 16, '{6, 3}', 1.0);

INSERT INTO blocks (model, position, cell, top) 
VALUES 
  ('spiral', '{ 0, 0 }', 'a', 't'),
  ('spiral', '{ 1, 0 }', 'c', 's'),
  ('spiral', '{ 2, 0 }', 'd', 'v'),
  ('spiral', '{ 3, 0 }', 'e', 'w'),
  ('spiral', '{ 4, 0 }', 'b', 't'),
  ('spiral', '{ 5, 0 }', 'g', 'x'),
  ('spiral', '{ 0, 1 }', 'i', 'u'),
  ('spiral', '{ 1, 1 }', 'k', null),
  ('spiral', '{ 2, 1 }', 'h', 'u'),
  ('spiral', '{ 3, 1 }', 'l', 'v'),
  ('spiral', '{ 4, 1 }', 'n', null),
  ('spiral', '{ 5, 1 }', 'f', 'v'),
  ('spiral', '{ 0, 2 }', 'm', 'v'),
  ('spiral', '{ 1, 2 }', 'o', 's'),
  ('spiral', '{ 2, 2 }', 'q', 't'),
  ('spiral', '{ 3, 2 }', 'j', 'x'),
  ('spiral', '{ 4, 2 }', 'r', 't'),
  ('spiral', '{ 5, 2 }', 'p', 'w');

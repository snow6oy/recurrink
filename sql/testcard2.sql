DELETE FROM blocks WHERE model = 'testcard2';
DELETE FROM models WHERE model = 'testcard2';

INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
VALUES ('testcard2', 12, '{4,3}', 0.5);

INSERT INTO blocks (model, position, cell) 
VALUES 
('testcard2', '{0, 0}', 'a'), 
('testcard2', '{1, 0}', 'b'), 
('testcard2', '{2, 0}', 'c'), 
('testcard2', '{3, 0}', 'd'), 

('testcard2', '{0, 1}', 'e'), -- row 2
('testcard2', '{1, 1}', 'f'), 
('testcard2', '{2, 1}', 'g'), 
('testcard2', '{3, 1}', 'h'), 

('testcard2', '{0, 2}', 'i'), 
('testcard2', '{1, 2}', 'j'), 
('testcard2', '{2, 2}', 'k'), 
('testcard2', '{3, 2}', 'l');

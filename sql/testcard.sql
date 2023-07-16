-- INSERT INTO models (model, uniqcells, blocksizeXY, scale) 
-- VALUES ('testcard', 15, '{10, 4}', 1.0);
DELETE FROM blocks WHERE model = 'testcard';

INSERT INTO blocks (model, position, cell) 
VALUES 
('testcard', '{0, 0}', 'x'), ('testcard', '{1, 0}', 'a'), 
('testcard', '{2, 0}', 'x'), ('testcard', '{3, 0}', 'b'), 
('testcard', '{4, 0}', 'x'), ('testcard', '{5, 0}', 'c'), 
('testcard', '{6, 0}', 'x'), ('testcard', '{7, 0}', 'd'), 
('testcard', '{8, 0}', 'x'), ('testcard', '{9, 0}', 'e'), 

('testcard', '{0, 1}', 'x'), ('testcard', '{1, 1}', 'A'), 
('testcard', '{2, 1}', 'x'), ('testcard', '{3, 1}', 'B'), 
('testcard', '{4, 1}', 'x'), ('testcard', '{5, 1}', 'C'), 
('testcard', '{6, 1}', 'x'), ('testcard', '{7, 1}', 'D'), 
('testcard', '{8, 1}', 'x'), ('testcard', '{9, 1}', 'E'), 

('testcard', '{0, 2}', 'x'), ('testcard', '{1, 2}', 'f'), 
('testcard', '{2, 2}', 'x'), ('testcard', '{3, 2}', 'g'), 
('testcard', '{4, 2}', 'x'), ('testcard', '{5, 2}', 'h'), 
('testcard', '{6, 2}', 'x'), ('testcard', '{7, 2}', 'i'), 
('testcard', '{8, 2}', 'x'), ('testcard', '{9, 2}', 'j'),

('testcard', '{0, 3}', 'x'), ('testcard', '{1, 3}', 'F'), 
('testcard', '{2, 3}', 'x'), ('testcard', '{3, 3}', 'G'), 
('testcard', '{4, 3}', 'x'), ('testcard', '{5, 3}', 'H'), 
('testcard', '{6, 3}', 'x'), ('testcard', '{7, 3}', 'I'), 
('testcard', '{8, 3}', 'x'), ('testcard', '{9, 3}', 'J'), 

('testcard', '{0, 4}', 'x'), ('testcard', '{1, 4}', 'k'), 
('testcard', '{2, 4}', 'x'), ('testcard', '{3, 4}', 'l'), 
('testcard', '{4, 4}', 'x'), ('testcard', '{5, 4}', 'm'), 
('testcard', '{6, 4}', 'x'), ('testcard', '{7, 4}', 'n'), 
('testcard', '{8, 4}', 'x'), ('testcard', '{9, 4}', 'o'), 

('testcard', '{0, 5}', 'x'), ('testcard', '{1, 5}', 'K'), 
('testcard', '{2, 5}', 'x'), ('testcard', '{3, 5}', 'L'), 
('testcard', '{4, 5}', 'x'), ('testcard', '{5, 5}', 'M'), 
('testcard', '{6, 5}', 'x'), ('testcard', '{7, 5}', 'N'), 
('testcard', '{8, 5}', 'x'), ('testcard', '{9, 5}', 'O'), 

('testcard', '{0, 6}', 'x'), ('testcard', '{1, 6}', 'p'), 
('testcard', '{2, 6}', 'x'), ('testcard', '{3, 6}', 'q'), 
('testcard', '{4, 6}', 'x'), ('testcard', '{5, 6}', 'r'), 
('testcard', '{6, 6}', 'x'), ('testcard', '{7, 6}', 'x'), 
('testcard', '{8, 6}', 'x'), ('testcard', '{9, 6}', 'x'), 

('testcard', '{0, 7}', 'x'), ('testcard', '{1, 7}', 'P'), 
('testcard', '{2, 7}', 'x'), ('testcard', '{3, 7}', 'Q'), 
('testcard', '{4, 7}', 'x'), ('testcard', '{5, 7}', 'R'), 
('testcard', '{6, 7}', 'x'), ('testcard', '{7, 7}', 'x'), 
('testcard', '{8, 7}', 'x'), ('testcard', '{9, 7}', 'x'), 

('testcard', '{0, 8}', 'x'), ('testcard', '{1, 8}', 's'), 
('testcard', '{2, 8}', 'x'), ('testcard', '{3, 8}', 't'), 
('testcard', '{4, 8}', 'x'), ('testcard', '{5, 8}', 'u'), 
('testcard', '{6, 8}', 'x'), ('testcard', '{7, 8}', 'x'), 
('testcard', '{8, 8}', 'x'), ('testcard', '{9, 8}', 'x'), 

('testcard', '{0, 9}', 'x'), ('testcard', '{1, 9}', 'S'), 
('testcard', '{2, 9}', 'x'), ('testcard', '{3, 9}', 'T'), 
('testcard', '{4, 9}', 'x'), ('testcard', '{5, 9}', 'U'), 
('testcard', '{6, 9}', 'x'), ('testcard', '{7, 9}', 'x'), 
('testcard', '{8, 9}', 'x'), ('testcard', '{9, 9}', 'x');

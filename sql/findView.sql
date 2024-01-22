-- SELECT model, v.ver , cell , shape , size , facing , top , p.ver , p.fill , bg , complimentary , p.opacity , s.fill , width , dasharray , s.opacity 
SELECT model, v.ver , cell , p.ver , p.fill , bg , complimentary , p.opacity
-- , s.fill , width , dasharray , s.opacity 
FROM views v, cells_new c, palette p
-- , strokes s AND c.sid = s.sid
-- geometry g, AND c.gid = g.gid
WHERE v.view = c.view
AND c.pid = p.pid
AND v.view = '16a9ff68ad976a98e4b7b1c8de77854b';
-- use gthumb find to *see* the view





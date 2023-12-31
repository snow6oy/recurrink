-- frequency of versions in views
SELECT count(ver), ver 
FROM views 
GROUP BY ver;

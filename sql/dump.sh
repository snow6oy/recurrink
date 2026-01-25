
cd /home/gavin/Dropbox/familia/recurrink/doc
pwd

pg_dump -d recurrink2 --column-inserts --data-only > db2_dump.sql
# pg_dump -d recurrink --column-inserts --data-only > db_dump.sql
# pg_retore -d recurrink2 < recurrink2.sql




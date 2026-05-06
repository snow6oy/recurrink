# backup data to cloud
# to start pCloud on ubuntu
# pcloudcc -u xyz@example.com -p 
cd /home/gavin/pCloudDrive/Art/recurrink/doc
pwd

pg_dump -d recurrink2 --column-inserts --data-only > db2_dump.sql
# pg_retore -d recurrink2 < recurrink2.sql




# backup data to cloud
# to start pCloud on ubuntu
# pcloudcc -u xyz@example.com -p 

# before restoring 
# cd sql
# psql -d recurrink2
# \i ddl_v2.sql
DUMPFILE=recurrink2.sql

if [[ "$OSTYPE" == "darwin"* ]]
then
  cd "/Users/gavin/pCloud Drive/Art/recurrink/doc"
else
  cd /home/gavin/pCloudDrive/Art/recurrink/doc
fi
pwd


if [ "$#" -ne 1 ]
then
  echo "usage: $0 dump|restore"
  exit
fi

if [ "$1" = 'dump' ]
then
  echo "dumping ${DUMPFILE}"
  # pg_dump -d recurrink2 --column-inserts --data-only > ${DUMPFILE}
  pg_dump -d recurrink2 > ${DUMPFILE}
elif [ "$1" = 'restore' ]
then
  echo "restoring ${DUMPFILE}"
  psql recurrink2 < ${DUMPFILE}
else
  echo "unknown command: $1"
fi

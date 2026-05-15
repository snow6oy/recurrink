# backup data to cloud
DUMPFILE=recurrink2.sql

if [ "$#" -ne 1 ]
then
  echo "usage: $0 dump|restore"
  exit
fi

if [[ "$OSTYPE" == "darwin"* ]]
then
  cd "/Users/gavin/pCloud Drive/Art/recurrink/doc"
else
  cd /home/gavin/pCloudDrive/Art/recurrink/doc
fi
pwd

if [ "$1" = 'dump' ]
then
  echo "dumping ${DUMPFILE}"
  pg_dump --clean -d recurrink2 > ${DUMPFILE}
elif [ "$1" = 'restore' ]
then
  echo "restoring ${DUMPFILE}"
  psql recurrink2 < ${DUMPFILE}
else
  echo "unknown command: $1"
fi

# t.block_data
psql -d recurrink2 \
     -c "DELETE FROM colors WHERE ver = 4 AND penam = 'zz'"
psql -d recurrink2 \
     -c "DELETE FROM layers WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'"
psql -d recurrink2 \
     -c "DELETE FROM rinks WHERE rinkid = 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'"

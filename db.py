import psycopg2
# port 5433 is tmp during transition from postgres 14 to 16

class Db:

  def __init__(self):
    ''' create connection to postgres
    '''
    connection = psycopg2.connect(dbname='recurrink', port=5433)
    connection.autocommit = True
    self.cursor = connection.cursor()

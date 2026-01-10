import psycopg2

class Db:

  def __init__(self):
    ''' create connection to postgres
    '''
    connection = psycopg2.connect(dbname='recurrink') #, port=5433)
    connection.autocommit = True
    self.cursor = connection.cursor()

class config:
  directory = {
       'rinks': '/home/gavin/Dropbox/familia/rinks',
        'pubq': '/home/gavin/Pictures/pubq',
    'palettes': '/home/gavin/.config/inkscape/palettes'
  }
'''
the
end 
'''

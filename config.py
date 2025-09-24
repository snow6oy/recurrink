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
       'rinks': '/Users/gavin/Dropbox/familia/rinks',
        'pubq': '/Users/gavin/Pictures/pubq',
    'palettes': '/Users/gavin/Library/Application Support/org.inkscape.Inkscape/config/inkscape/palettes'
  }
'''
the
end 
'''

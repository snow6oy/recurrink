import psycopg2

class Db:

  def __init__(self):
    ''' USE DB2

    connection = psycopg2.connect(dbname='recurrink') #, port=5433)
    connection.autocommit = True
    self.cursor = connection.cursor()
    '''
    pass

class Db2:

  def __init__(self):
    ''' create connection to postgres
    '''
    connection  = psycopg2.connect(dbname='recurrink2')
    connection.autocommit = True
    self.cursor = connection.cursor()

class config:
  directory = {
       'rinks': '/Users/gavin/pCloud Drive/Art/rinks',
       'plotq': '/Users/gavin/Pictures/plotq',
    'palettes': '/Users/gavin/Library/Application Support/org.inkscape.Inkscape/config/inkscape/palettes'
  }
  _directory = {  # ubuntu paths
       'rinks': '/home/gavin/pCloud/Art/rinks',
       'plotq': '/home/gavin/Pictures/plotq',
    'palettes': '/home/gavin/.config/inkscape/palettes'
  }
'''
the
end 
'''


ALTER TABLE views ADD pubdate DATE;

UPDATE views SET pubdate=CURRENT_DATE WHERE view = 'e4681aa9b7aef66efc6290f320b43e55';


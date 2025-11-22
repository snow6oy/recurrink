from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, RootModel, ValidationError, field_serializer
from typing import Literal, Dict, Optional
# see hack in sitelib site-packages/pydantic_extra_types/__init__.py 
from pydantic_extra_types import Color      

class Stroke(BaseModel):
  fill       : Color
  dasharray  : int = None
  opacity    : Decimal = Field(gt=0, le=1)  # should default to 1 ?
  width      : float = None

  @field_serializer('fill')
  def serializerFill(self, fill: Color):
    return fill.as_hex(format='long')

  @field_serializer('opacity')
  def serializerOpacity(self, opacity: Decimal):
    return float(opacity)

class Color(BaseModel):
  opacity   : Decimal = Field(gt=0, le=1)
  fill      : Color
  background: Optional[Color] = None

  @field_serializer('fill')
  def serializerFill(self, fill: Color):
    return fill.as_hex(format='long')

  @field_serializer('background')
  def serializerBackground(self, background: Color):
    if background is not None:
      return background.as_hex(format='long')

  @field_serializer('opacity')
  def serializerOpacity(self, opacity: Decimal):
    return float(opacity)

class Geoname(str, Enum):
  ''' names truncated because original storage was tab separated
  '''
  square  = 'square'
  line    = 'line'
  circle  = 'circle'
  triangl = 'triangl'
  diamond = 'diamond'
  gnomon  = 'gnomon'
  parabol = 'parabol'
  # sqring   = 'sqring' sqring aint a thing

class Geom(BaseModel, use_enum_values=True):
  name: Geoname
  size: Literal['small', 'medium', 'large']
  facing: Literal['C', 'N', 'E', 'S', 'W', 'NE', 'NW', 'SE', 'SW']
  top: bool

class Cell(BaseModel):
  geom  : Geom
  color : Color
  stroke: Optional[Stroke] = None

class Cells(RootModel):
  root : Dict[str, Cell]

  def __iter__(self):
    return iter(self.root)

  def __getitem__(self, item):
    return self.root[item]

class InputValidator:

  def validate(self, incoming):
    ''' examples to access model directly
    print(f"{float(model['a'].color.opacity)=}")             # Decimal
    print(f"{model['a'].color.fill.as_hex(format='long')=}") # Color
    print(f"{model['a'].stroke.dasharray=}")                 # int
    '''
    try:
      model = Cells(incoming)        # pydantic model will apply model constraints
    except ValidationError as err:
      return err  
    cells = model.model_dump()  # obtain clean dictionary output with serializers
    return cells

'''
the
end
'''

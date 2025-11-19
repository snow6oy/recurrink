from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, RootModel, field_serializer
from typing import Literal, Dict
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
  background: Color

  @field_serializer('fill')
  def serializerFill(self, fill: Color):
    return fill.as_hex(format='long')

  @field_serializer('background')
  def serializerBackground(self, background: Color):
    return background.as_hex(format='long')

  @field_serializer('opacity')
  def serializerOpacity(self, opacity: Decimal):
    return float(opacity)

class Geoname(str, Enum):
  square   = 'square'
  line     = 'line'
  circle   = 'circle'
  triangl  = 'triangl'
  diamond  = 'diamond'
  gnomon   = 'gnomon'
  parabola = 'parabola'
  sqring   = 'sqring'

class Geom(BaseModel, use_enum_values=True):
  name: Geoname
  size: Literal['small', 'medium', 'large']
  facing: Literal['C', 'N', 'E', 'S', 'W']
  top: bool

class Cell(BaseModel):
  geom  : Geom
  color : Color
  stroke: Stroke

class Cells(RootModel):
  root : Dict[str, Cell]

  def __iter__(self):
    return iter(self.root)

  def __getitem__(self, item):
    return self.root[item]

class InputValidator:

  def validate(self, incoming):
    model = Cells(incoming)        # pydantic model will apply model constraints
    ''' see also t.validator
    print(f"{float(model['a'].color.opacity)=}")             # Decimal
    print(f"{model['a'].color.fill.as_hex(format='long')=}") # Color
    print(f"{model['a'].stroke.dasharray=}")                 # int
    '''
    cells = model.model_dump()  # obtain clean dictionary output with serializers
    return cells

'''
the
end
'''

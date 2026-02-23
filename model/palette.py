import pprint
from config import *

class SvgPalette:
  ''' tool for generating palettes/*.html
  '''

  def render(self, fn, palette):
    head = self.htmlHeader()
    data = self.tableRows(palette)
    tail = self.htmlFooter()
    with open(f"palettes/{fn}.html", "w") as outfile:
      outfile.write(head + data + tail)

  def hexRgb(self, hexstr):
    ''' #66ff00 > 102 255 0
        converts hex to rgb using base 16
    '''
    if len(hexstr) == 4:  # expand shorthand
      hexitems = [hexstr[1] * 2, hexstr[2] * 2, hexstr[3] * 2]
    else:
      hexitems = [hexstr[1:3], hexstr[3:5], hexstr[5:]]
    return [int(h,16) for h in hexitems]

  def tableRows(self, palette):
    data = str()
    for entry in palette:
      fg, op, bg = entry
      r,   g,  b = self.hexRgb(fg)
      data += f'''  <tr>
        <td style="width:30%">{fg}</td>
        <td style="background-color:{fg};width:10%" />
        <td style="width:20%">{op}</td>
        <td style="width:30%">{bg}</td>
        <td style="background-color:{bg};width:10%">
          <div style="color: rgba({r}, {g}, {b}, {op})">&#9673;</div>
        </td>
      </tr>'''
    return data

  def htmlHeader(self):
    head = """<html>
<head>
<!-- begin snippet: js hide: false console: true babel: null babelPresetReact: false babelPresetTS: false -->

<!-- language: lang-js
  { name: 'Name', index: 0, isFilter: false },
  { name: 'Country', index: 1, isFilter: true } -->

<script>
    const myFunction = () => {
      const columns = [
        { name: 'Foreground', index: 0, isFilter: true  },
        { name: 'Opacity',    index: 1, isFilter: false },
        { name: 'Background', index: 2, isFilter: false }
      ]
      const filterColumns = columns.filter(c => c.isFilter).map(c => c.index)
      const trs = document.querySelectorAll(`#myTable tr:not(.header)`)
      const filter = document.querySelector('#myInput').value
      const regex = new RegExp(escape(filter), 'i')
      const isFoundInTds = td => regex.test(td.innerHTML)
      const isFound = childrenArr => childrenArr.some(isFoundInTds)
      const setTrStyleDisplay = ({ style, children }) => {
        style.display = isFound([
          ...filterColumns.map(c => children[c]) // <-- filter Columns
        ]) ? '' : 'none'
      }
      
      trs.forEach(setTrStyleDisplay)
    }
</script>
<style>
    input#myInput { width: 220px; }
    table#myTable { width: 100%; }
    table#myTable th { text-align: left; padding: 20px 0 10px; }
</style>
<body>
    <input 
      type="text" 
      id="myInput" 
      onkeyup="myFunction()" 
      placeholder="Filter by foreground.." 
      title="Enter an RGB value.">

<table border id="myTable">
  <tr class="header">
    <th colspan="2">Foreground</th>
    <th>Opacity</th>
    <th colspan="2">Background</th>
  </tr>
"""
    return head

  def htmlFooter(self):
    tail = """</table>
</body>
<!-- 
https://stackoverflow.com/questions/51187477/how-to-filter-a-html-table-using-simple-javascript -->
</html>"""
    return tail

if __name__ == '__main__':
  '''
  ./recurrink init -p uniball
  ./recurrink build -v1
  '''

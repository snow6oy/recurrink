``` 
cd ~/code/recurrink
source v/bin/activate
screen -S rink
python -m unittest t.Test.test_n
```

# Order of Execution
Not numeric after all *face palm*
```
t.layout.Test.test_1
t.layout.Test.test_10
t.layout.Test.test_11
t.layout.Test.test_12
t.layout.Test.test_13
t.layout.Test.test_14
t.layout.Test.test_15
t.layout.Test.test_16
t.layout.Test.test_2
t.layout.Test.test_3
```

# Test Coverage

```
cell/
y	cell/data.py
y	cell/layer.py
y 	cell/geometry.py

cell/shape/
y	cell/shape/rectangle.py
y	cell/shape/parabola.py
y	cell/shape/gnomon.py

block/
y	block/data.py
y	block/make.py
n	block/styles.py
y	block/spiral.py
y	block/meander.py
y	block/tmpfile.py
y	block/palette.py

	model/
n	model/db.py
y	model/svg.py
y	model/data.py
y	model/linear.py
-	model/palette.py
```


## Regression

an example rink for each model
5 rinks have stroke widths that cannot scale down to A4
```
declare -a arr=(
  "01772cb0944aedb65e855223814ff59c"
  "12f56f3aacd157f0928b58a8db5a704f"
  "080d7e076b2f7e031158218e79013b72"
  "15ff3a9dd88436a0fffa87aad8904784"
  "0008b5f11d15cab4ec167657ec9b8e48" # sw 6
  "06a0e466d56aa560b3809cf137f2ed7a"
  "5483db8069a3ab777585ab24868e32b3" # sw 8
  "0d98fa16d3384fd366afb1d9ca40efeb"
  "0b1e90af76f7fd922c1e14390237d6ee" # sw 9
  "347a8b995c471c03dee5e0d05df75c87" # sw 10
  "0d977718dff002b1dab7cdee7d919c03"
  "03563ece1beb351ea79314f130b7a1ad"
  "4a6dd97d67fbb6b34981479299e7ada8"
  "080469235495bce65c8f8c19df9ba3c2"
  "088485fe0310221082a272cf03ab29e2"
  "5bd0d8405d453b47f0ba8359b71d750e" # sw 10
  "02b7defd538d1602fbf35d27612f9021"
  "08d971a3c0f2919aa1b29897a9611647")

# clone and make svg for A4 or not
for i in "${arr[@]}"
do
   echo "$i"
   ./recurrink clone -v"$i"
   ./recurrink update --a4
done
```

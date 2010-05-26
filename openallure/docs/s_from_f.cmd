copy ..\openallure.cfg .
copy rst\* source\txt\*
type ..\CHANGES.txt >> source\txt\CHANGES.rst
type ..\ethics_notice.txt >> source\txt\ethics_notice.rst
type ..\LICENSE.txt >> source\txt\LICENSE.rst
type ..\README.txt >> source\txt\README.rst
python dressCfg.py
d:\python25\pongg\scripts\sphinx-build -E -a -b html source html

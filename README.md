NorthEuraLex: website
=====================

setup
=====

How to install:

1. Create venv in main dir
2. Install clld with pip
<code>pip install clld</code>
3. Change dir into northeuralex
<code>cd northeuralex</code>
4. Install northeuralex app with
<code>pip install -e .</code>
5. Start CLLD webapp with
<code>pserve development.ini</code>
   
   
To update database:
1. Download desired CLDF dataset
2. Recreate database with:
   <code>clld initdb --glottolog PATH/TO/glottolog/glottolog/ --cldf PATH/TO/northeuralex/cldf/cldf-metadata.json development.ini</code>
3. Rerun pserve 
<code>pserve development.ini</code>


Glottolog files can be found at:
https://doi.org/10.5281/zenodo.596479

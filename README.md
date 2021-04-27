# cldf_northeuralex

How to install:

1. Create venv in main dir
2. Install clld with pip
3. Change dir into northeuralex
4. Install northeuralex app with
   pip install -e .
5. Start CLLD webapp with
   pserve development.ini
   
   
To update database:
1. Download desired CLDF dataset
2. Recreate database with:
   clld initdb --glottolog PATH/TO/glottolog/glottolog/ 
   --cldf PATH/TO/northeuralex/cldf/cldf-metadata.json 
   development.ini
3. Rerun pserve 

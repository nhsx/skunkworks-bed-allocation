#!/bin/bash

cd ../../fake_data_generation
read -p "This script will remove any previously generated fake_data_files. Continue? [yN] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Aborting script"
    exit 1
fi
rm -fr fake_data_files
python generate_fake_data.py -nr 20000
mv fake_data_files/* ../data/

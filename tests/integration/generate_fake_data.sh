#!/bin/bash

cd ../../fake_data_generation
rm -fr fake_data_files
python generate_fake_data.py -nr 20000
mv fake_data_files/* ../data/
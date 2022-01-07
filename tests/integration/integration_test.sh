#!/bin/bash

# Crude end-to-end integration test
# Requires installation of modules in development mode

echo "Creating fake data:"
./generate_fake_data.sh

if [ $? -eq 0 ] 
then 
  echo "Successfully created fake data" 
else 
  echo "Could not create fake data"
  exit 1
fi

echo "Training time series model:"
python generate_time_series_model.py

if [ $? -eq 0 ] 
then 
  echo "Successfully trained time series model" 
else 
  echo "Could not train time series model"
  exit 1
fi

echo "Generating patient split with number of samples 10:"
python ../../app/app/data/get_forecast_split.py -n 10

if [ $? -eq 0 ] 
then 
  echo "Successfully generated patient split" 
else 
  echo "Could not generate patient split"
  exit 1
fi

echo "Generating forecast percentiles:"
python ../../app/app/data/get_forecast_percentiles.py

if [ $? -eq 0 ] 
then 
  echo "Successfully generated patient forecast percentiles" 
else 
  echo "Could not generate patient forecast percentiles"
  exit 1
fi

echo "Creating virtual hospital:"
python generate_hospital.py

if [ $? -eq 0 ] 
then 
  echo "Successfully created virtual hospital" 
else 
  echo "Could not create virtual hospital"
  exit 1
fi

echo "Running UI frontend. You will need to manually verify the application is correctly running."

python ../../app/run.py

echo "Integration test complete"
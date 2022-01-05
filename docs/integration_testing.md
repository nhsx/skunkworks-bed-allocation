# Integration testing

Once you have installed this tool in development mode and activated your virtual environment, you can execute end-to-end integration test by running from the main project directory:

```bash
cd tests/integration
./integration_test.sh
```

This will perform the following actions:

1. Create virtual hospital
2. Generate fake data
3. Generate Time Series forecast
5. Generate random patient split attributes
6. Generate forecast percentiles
7. Run the UI

You will need to visit the UI URL and check the app is performing as expected.
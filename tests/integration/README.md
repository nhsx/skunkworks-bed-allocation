# Integration testing

Once you have installed this tool in development mode and activated your virtual environment, you can execute end-to-end integration test by running from the main project directory:

```bash
cd tests/integration
./integration_test.sh
```

This will perform the following actions:

1. Generate fake data (respond Y or y when prompted)
2. Generate Time Series forecast
3. Generate patient attributes
4. Generate forecast percentiles
5. Create virtual hospital
6. Run the UI

You will need to visit the UI URL and check the app is performing as expected.
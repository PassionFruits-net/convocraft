# ConvoCraft

# Persistence settings

In `config.yaml`, there's an fsspec path to where files are persisted
in `persistence.base`. Depending on the filesystem / url scheme you
use, you will have to provide cloud service authentication tokens of
some sort. For azure blob storage, `az:`-urls, set:

```
export AZURE_STORAGE_CONNECTION_STRING=""
```

### Run the app
    streamlit run app/main.py

### Debug mode 
debug mode uses fake data for outline and convo generation (but the audio generation functions still make calls to the OpenAI API)

    export DEBUG_MODE="true"
    streamlit run app/main.py

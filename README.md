# ConvoCraft

## Preparations

### Install dependencies

```
pip install -r requirements.txt
```

### Persistence settings

In `config.yaml`, there's an fsspec path to where files are persisted
in `persistence.base`. Depending on the filesystem / url scheme you
use, you will have to provide cloud service authentication tokens of
some sort. For azure blob storage, `az:`-urls, set:

```
export AZURE_STORAGE_CONNECTION_STRING="your-connection-string-here"
```

### OpenAI API account

```
export OPENAI_API_KEY="your-api-key-here"
```

### Debug mode 
Debug mode uses fake data for outline and convo generation (but the audio generation functions still make calls to the OpenAI API)

```
export DEBUG_MODE="true"
```

## Run the app

```
streamlit run app/main.py
```

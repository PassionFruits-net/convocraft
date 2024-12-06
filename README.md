# ConvoCraft

### Run the app
    streamlit run app/main.py

### Debug mode 
debug mode uses fake data for outline and convo generation (but the audio generation functions still make calls to the OpenAI API)

    export DEBUG_MODE="true"
    streamlit run app/main.py

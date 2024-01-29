# Brain Genomics TWAS WebApp 
Simple web application for parsing TWAS results (regional brain volumes in the UK Biobank) 

_last update: Jan 29, 2024 (NH)_

## How to Run

App was developed using Python version 3.7.2

Tasks to do once: 
1) Download the _input_data_ folder (from Vanderbilt Box; available upon [request](https://vanderbilt.box.com/s/q43u7cdgz4vb6qgpyt4qwacjotkcbew2)) to the main folder
2) Create a Python virtual environment: `python -m venv venv_dash`
3) Activiate it and install the included dependencies using pip: `source venv_dash/bin/activate; pip install -r dash_reqs.txt`

Running the app: 
1) Make sure the virtual environment is activate (`source venv_dash/bin/activate` to do so)
2) Run the app: `python app.py`
3) Copy the local URL to your brower (example URL: http://127.0.0.1:8050/)
4) Interact with the webapp!

Closing the app: 
1) Close the window as you would for a website
2) Deactivate the virtual environment (`deactivate`) 

# Brain Genomics TWAS WebApp 
Simple web application for parsing TWAS results from _Hoang, et al._ (regional brain volumes in the UK Biobank) 

_last code update: Jan 30, 2024_

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

## WebApp Layout

Home (**TWAS Table**) page - for exploring all or a subset of the TWAS results 

<img width="1469" alt="s1" src="https://github.com/nhunghoang/Brain-Genomics-TWAS-WebApp/assets/23412134/30dc4acc-98ce-47fb-a939-e6b236a813a5">

**Summaries by Gene** page - for exploring the TWAS, GWAS, and BioVU associations of a specific gene 

<img width="1465" alt="s2" src="https://github.com/nhunghoang/Brain-Genomics-TWAS-WebApp/assets/23412134/e990f27c-7595-4b89-8b21-53f39328f0d6">
<img width="1445" alt="s3" src="https://github.com/nhunghoang/Brain-Genomics-TWAS-WebApp/assets/23412134/66a7a040-c00d-443f-8b9e-550a13e5d838">


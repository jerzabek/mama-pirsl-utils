# Photo processing script

## Description

A script that receives photos as an input and converts them to a 16:9 ratio (with proper padding) and adds a watermark at the center of the image.

## Installation

Make sure you have an installed version of python >= 3.10.12 as well as pip.
Create a virtual environment (venv) in order to install the requirements:
```
python3 -m venv PATH_TO_VENV
```

Load the venv:
```
source PATH_TO_VENV/bin/activate
```

Install the requirements:
```
pip install -r requirements.txt
```

## Usage

Run the script as follows:
```
python3 main.py -r PHOTO_FOLDER -w PATH_TO_WATERMARK_PHOTO
```

You can call the script and invoke the help function in order to see more options.

```
python3 main.py -h
```

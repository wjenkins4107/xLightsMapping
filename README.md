# xLightsMapping
xLights Python Mapping Tool

Author: Bill Jenkins  
Date: 06/16/2025 
Version: 1.0

# Environment

Windows 11 64bit  
Python: v3.11.1  
xLights: v2025.06 64bit  

# Requirements:
- xLights v2025.05+
- Python v3.11.1+
  - download and install python from python.org

# Imports
- import tkinter as tk
- from tkinter import ttk
- from tkinter import messagebox
- import xml.etree.ElementTree as ET
- import sys
- import os
- import datetime as dt
- import logging
- import argparse 

# Script: map_models_submodels.py
A script to create a mapping file using like models of a primary model and all of its submodels using a GUI interface.
An xLights show folder is entered. Then from the models in the xlights_rgbeffectx.xml file in the show folder a primary model is selected.
Then either like models are selected to map manually or by checking the match by model name to map.\ 
*NOTE* The match is only for models that have the following trailing characters "-0123456789".\
- A mapping file is then created in the show folder using the following format:\
ex: "03.15.0Mod SHOWSTOPPER SNOWFLAKE_mapping_2025_06_16.xmap"
- A log file is created in the show folder using the following format:\
ex: "map_models_submodels_2025_06_16.log"


## Arguments:
    -l    --logging               ; Logging Level                ; default 30 ; Choices [0, 10, 20, 30, 40, 50]    ; Required = False
                                                                 0=NOTSET, 10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL
## Example(s):
    python map_models_submodels.py
    python map_models_submodels.py -l 10

## Images:
Show Folder Window\
![Mapping Show Folder Window](https://github.com/user-attachments/assets/32196fde-0803-4406-958c-efd51fade528)\
Select Primary Model Window\
![Mapping Select Primary Model Window](https://github.com/user-attachments/assets/35df5fd0-d568-407f-a37f-b32cc51724c4)\
Select Mapping Model Window\
![Mapping Select Mapping Models](https://github.com/user-attachments/assets/e28757af-b07d-4964-be35-4a426f08b15b)\
Sample Status Message\
![Mapping Status Message](https://github.com/user-attachments/assets/7ba0c1f4-3133-42de-b402-e24788e16fee)




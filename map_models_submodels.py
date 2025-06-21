#!/usr/bin/env python

# Name: map_models_submodels.py
# Purpose: Create an xLights Map of a Model and Submodels to other like Models and SubModels 
# Author: Bill Jenkins
# Version: v1.0
# Date: 06/16/2025

###########################
# Imports                 #
###########################
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import xml.etree.ElementTree as ET
import platform
import sys
import os
import winreg
import datetime as dt
import logging
import argparse

########################################
# Logging setup
########################################
def setup_logging(logging_level):
    LOG_FILE = "map_models_submodels_" + str(dt.date.today()).replace('-', '_') + ".log"
    logging.basicConfig(
        level = logging_level,
        format = '%(asctime)s - %(levelname)s - %(threadName)s - %(filename)s:%(lineno)d - %(message)s',
        handlers = [logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)]
        )

###############################
# Read Registry Value
###############################
def read_registry_value(hive, subkey, value_name):
    """
    Reads a value from the Windows Registry.

    Args:
        hive: The root key (e.g., winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER).
        subkey: The path to the registry key (e.g., "SOFTWARE\\Microsoft\\Windows\\CurrentVersion").
        value_name: The name of the value to read (e.g., "ProgramFilesDir").

    Returns:
        The data of the specified registry value, or None if the key or value is not found.
    """

    try:
        # Open the registry key
        key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_READ)

        # Query the value
        value, reg_type = winreg.QueryValueEx(key, value_name)

        # Close the key
        winreg.CloseKey(key)

        return value

    except FileNotFoundError:
        logging.error(f"Registry key or value not found: {subkey}\\{value_name}")
        return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None


###############################
# Calculate XY Coordinates
###############################
def calcxycoord(window, location, w, h):
    #
    ws = window.winfo_screenwidth() # width of the screen
    hs = window.winfo_screenheight() # height of the screen
    n_off = 30
    s_off = 90
    e_off = 30
    w_off = 30
    l = location.lower()
    if (l in ['c', 'center']):
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
    elif (l in ['n', 'north']):
        x = (ws/2) - (w/2)
        y = n_off
    elif (l in ['ne', 'northeast']):
        x = (ws - (w + e_off))
        y = n_off
    elif (l in ['e', 'east']):
        x = (ws - (w + e_off))
        y = (hs/2) - (h/2)    
    elif (l in ['se', 'southeast']):
        x = (ws - (w + e_off))
        y = (hs - (h + s_off))
    elif (l in ['s', 'south']):
        x = (ws/2) - (w/2)
        y = (hs - (h + s_off))    
    elif (l in ['sw', 'southwest']):
        x = w_off
        y = (hs - (h + s_off))
    elif (l in ['w', 'west']):
        x = w_off
        y = (hs/2) - (h/2)
    elif (l in ['nw', 'northwest']):
        x = w_off
        y = n_off
    else:
        x = 0
        y = 0
        
    return(x, y)
    
############################
# Message Box
############################
def msgbox(winid, msg):
    messagebox.showinfo(winid, msg)

########################################
# Get Models Submodel(s)
########################################
def get_models_submodels(rgbeffects_file):
    # RGB Effects Tree
    effects_tree = ET.parse(rgbeffects_file)
    # RGB Effects Root
    effects_root = effects_tree.getroot()
    logging.debug(f"xlights_rgbeffects.xml = {rgbeffects_file}")

    models_submodels = {}
    for model in effects_root.findall("models/model"):
        model_name = model.get("name", "")
        description = model.get("Description", "")
        logging.debug(f"*" * 50)
        logging.debug(f"Model Name: {model_name} {description}")
        logging.debug(f"*" * 50)
        model_info = {}
        submodels_list = []
        for submodel in model.findall("subModel"):
            submodel_name = submodel.get("name")
            # Not Comment?
            if (submodel_name and submodel_name[0] != "*"):
                submodels_list.append(submodel_name)
                logging.debug(f"+++ SubModel Name = {submodel_name}")
        # Update Model Information
        models_submodels[model_name] = {"description": description, "submodels": submodels_list}
    return(models_submodels)

###############################
# Create Mapping File
###############################
def create_mapping_file(mapping_file_name: str, primary_model: str, submodels_list: list, mapping_models: list):
    logging.debug(f"mapping_file_name: {mapping_file_name}")
    logging.debug(f"primary_model: {primary_model}")
    for mapping_model in mapping_models:
        logging.debug(f"mapping_model: {mapping_model}")
    with open(mapping_file_name, 'w') as f:
        f.write("false\n")
        f.write(str(len(mapping_models)) + "\n")
        for mapping_model in mapping_models:
            f.write(mapping_model + "\n")
        for mapping_model in mapping_models:
            f.write(mapping_model + "\t\t\t" + primary_model + "\twhite\n")
            for submodel in submodels_list:
                f.write(mapping_model + "\t" + submodel + "\t\t" + primary_model + "/" + submodel + "\twhite\n")
    logging.info(f"Mapping File {mapping_file_name} created...")
    msgbox("Info:", f"Mapping File {mapping_file_name} created...")
    return

###############################
# Map Select Button
###############################
def map_select_button(map_win, treev_top, primary_model: str, models_submodels: list):
    # Get Selected Item(s)
    mapping_models = []
    selected_items = treev_top.selection()
    for item in selected_items:
        logging.debug(f"Selected Item: {item}")
        values = treev_top.item(item, 'values')
        logging.debug(f"values: {values}")
        mapping_model = values[0]
        # Remove Selection on Item
        treev_top.selection_remove(item)
        # Select Mapping Models
        mapping_models.append(mapping_model) 
    if mapping_models:
        # Create Mapping File
        mapping_file_name = show_folder + "/" + primary_model + "_mapping_" + str(dt.date.today()).replace('-', '_') + ".xmap"
        model_info = models_submodels.get(primary_model)
        submodels = model_info.get("submodels", [])
        create_mapping_file(mapping_file_name, primary_model, submodels, mapping_models)
        map_win.destroy()
    else:
        logging.info(f"No Mapping Models Selected...")
        msgbox("Info:", f"No Mapping Models Selected...")
    return

###############################
# Select Mapping Models Window
###############################
def select_mapping_models_window(pri_win, primary_model: str, models_submodels: dict):
    # Define Toplevel
    map_win = tk.Toplevel(pri_win)
    map_win.title('Select Mapping Models')
    # Set Window Width and Height
    w = 830 # width for map_win
    h = 640 # height for map_win
    # Calculate Window Cordinates
    (x, y) = calcxycoord(map_win, "east", w, h)
    map_win.geometry('%dx%d+%d+%d' % (w, h, x, y))
    map_win.lift()
    # Set Style Theme
    style_s = ttk.Style()
    style_s.theme_use('clam')
    # Create a primary frane
    pri_frame = ttk.Frame(map_win, height = 20, width = 400)
    pri_frame.grid(row = 0, column = 0, padx = 5, pady = 5)    
    # Create a top frame
    top_frame = ttk.Frame(map_win, height = 400, width = 400)
    top_frame.grid(row = 1, column = 0, padx = 5, pady = 5)
    # Create a frame for the buttons
    buttons_frame = ttk.Frame(map_win, height = 50, width = 400)
    buttons_frame.grid(row = 2, column = 0, padx = 5, pady = 5)
    # Create a frame for the CTRL Key
    ctrl_key_frame = ttk.Frame(map_win, height = 20, width = 400)
    ctrl_key_frame.grid(row = 3, column = 0, padx = 5, pady = 5)

    # Primary Model Label 
    primary_model_label = tk.Label(pri_frame, text="Primary Model:", justify=tk.RIGHT)
    primary_model_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    # Primary Model Variable
    primary_model_var = tk.StringVar()
    primary_model_var.set(primary_model)
    primary_model_label = tk.Label(pri_frame, textvariable=primary_model_var, justify=tk.LEFT)
    primary_model_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    # Define Columns and Headings
    columnslist = []
    for i in range(1, 3):
        columnslist.append("C" + str(i))
    # Add a Top Treeview
    treev_tree = ttk.Treeview(top_frame, selectmode='extended', column=columnslist, show='headings', height=20)
    treev_tree.column("# 0", width = 0, stretch = "no") # Hidden
    treev_tree.heading("# 0", text = "")
    treev_tree.column("C1", width = 400, anchor='w')
    treev_tree.heading("C1", text = "Model")
    treev_tree.column("C2", width = 400, anchor='w')
    treev_tree.heading("C2", text = "Description")
    treev_tree.grid(row=0, column=0, sticky = "nsew")
    # Add Vertical Scrollbar
    treev_tree_vscrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL, command=treev_tree.yview)
    treev_tree.configure(yscroll=treev_tree_vscrollbar.set)
    treev_tree_vscrollbar.grid(row=1, column=3, sticky = 'nsew')

    # Build Models List
    models_values_list = []
    for model, model_info in models_submodels.items():
        logging.info(f"model: {model}")
        if (model != primary_model):
            description = model_info.get("description", "")
            logging.info(f"description: {description}")
            models_values_list.append([model, description])
    models_values_list.sort()
    for model_values in models_values_list:
        treev_tree.insert('', tk.END, values=model_values)

    # Primary Button
    primary_button = tk.Button(buttons_frame, text="Map Selected", command=lambda: map_select_button(map_win, treev_tree, primary_model, models_submodels))
    primary_button.config( width = 15 )
    primary_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    # Close Button
    close_button = tk.Button(buttons_frame, text="Close", command=map_win.destroy)
    close_button.config( width = 15 )
    close_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")
    # 
    ctrl_key_label = tk.Label(ctrl_key_frame, text="Hold down the CTRL key to select multiple models", justify=tk.CENTER)
    ctrl_key_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    

    map_win.mainloop()
    return()

def remove_trailing_chars(text: str):
    # Remove Trailing Chars
    result = text.rstrip('-0123456789')
    return result

########################
# Primary Select Button
########################
def primary_select_button(pri_win, treev_tree, models_submodels: dict, match_model_name_var: bool):
    # Get Selected Item(s)
    selected_items = treev_tree.selection()
    for item in selected_items:
        logging.debug(f"Selected Item: {item}")
        values = treev_tree.item(item, 'values')
        logging.debug(f"values: {values}")
        primary_model = values[0]
        # Remove Selection on Item
        treev_tree.selection_remove(item)
        # Get Primary Model subModels
        model_info = models_submodels.get(primary_model)
        submodels = model_info.get("submodels", "")
        # Match by Model Name?
        if match_model_name_var.get():
            # Remove Trailing Numbers & "-"
            check_primary_model = remove_trailing_chars(primary_model)
            mapping_models = []
            for mapping_model, mapping_model_info in models_submodels.items():
                check_mapping_model = remove_trailing_chars(mapping_model)
                if (check_primary_model == check_mapping_model and primary_model != mapping_model):
                    logging.debug(f'mapping_model: {mapping_model}')
                    mapping_models.append(mapping_model)
            if mapping_models:
                # Create Mapping File
                mapping_file_name = show_folder + "/" + primary_model + "_mapping_" + str(dt.date.today()).replace('-', '_') + ".xmap"
                create_mapping_file(mapping_file_name, primary_model, submodels, mapping_models)
            else:
                logging.info(f"No Matching Mapping Models Selected...")
                msgbox("Info:", f"No Matching Mapping Models Selected...")
        else:
            # Select Mapping Models 
            select_mapping_models_window(pri_win, primary_model, models_submodels)

###############################
# Select Primary Model Window
###############################
def select_primary_model_window(parent, rgbeffects_file: str, models_submodels: dict):
    # Define Toplevel
    pri_win = tk.Toplevel(parent)
    pri_win.title('Select Primary Model')
    # Set Window Width and Height
    w = 830 # width for pri_win
    h = 650 # height for pri_win
    # Calculate Window Cordinates
    (x, y) = calcxycoord(pri_win, "center", w, h)
    pri_win.geometry('%dx%d+%d+%d' % (w, h, x, y))
    pri_win.lift()
    # Set Style Theme
    style_s = ttk.Style()
    style_s.theme_use('clam')
 
    # Create a top frame
    top_frame = ttk.Frame(pri_win, height = 20, width = 400)
    top_frame.grid(row = 0, column = 0, padx = 5, pady = 5)
    # Create a mid frame
    tree_frame = ttk.Frame(pri_win, height = 400, width = 400)
    tree_frame.grid(row = 1, column = 0, padx = 5, pady = 5)
    # Create a frame for the buttons
    buttons_frame = ttk.Frame(pri_win, height = 50, width = 400)
    buttons_frame.grid(row = 2, column = 0, padx = 5, pady = 5)

    # rgbeffects Label 
    rgbeffects_label = tk.Label(top_frame, text="RGB Effects File", justify=tk.RIGHT)
    rgbeffects_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    # rgbeffects Variable
    rgbeffects_file_var = tk.StringVar()
    rgbeffects_file_var.set(rgbeffects_file)
    rgbeffects_file_label = tk.Label(top_frame, textvariable=rgbeffects_file_var, justify=tk.LEFT)
    rgbeffects_file_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
    
    # Create Match Model Name CheckBox
    match_model_name_var = tk.BooleanVar()
    match_model_name = tk.Checkbutton(top_frame, text="Match by Model Name", variable=match_model_name_var)
    match_model_name.grid(row=1, column=1, padx=10, pady=10, sticky="w")
    
    # Define Columns and Headings
    columnslist = []
    for i in range(1, 3):
        columnslist.append("C" + str(i))
    # Add a Top Treeview
    treev_tree = ttk.Treeview(tree_frame, selectmode='browse', column=columnslist, show='headings', height=20)
    treev_tree.column("# 0", width = 0, stretch = "no") # Hidden
    treev_tree.heading("# 0", text = "")
    treev_tree.column("C1", width = 400, anchor='w')
    treev_tree.heading("C1", text = "Model")
    treev_tree.column("C2", width = 400, anchor='w')
    treev_tree.heading("C2", text = "Description")
    treev_tree.grid(row=0, column=0, sticky = "nsew")
    # Add Vertical Scrollbar
    treev_tree_vscrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=treev_tree.yview)
    treev_tree.configure(yscroll=treev_tree_vscrollbar.set)
    treev_tree_vscrollbar.grid(row=0, column=3, sticky = 'nsew')

    # Build Models List
    models_values_list = []
    for model, model_info in models_submodels.items():
        logging.debug(f"model: {model}")
        description = model_info.get("description", "")
        logging.debug(f"description: {description}")
        models_values_list.append([model, description])
    models_values_list.sort()
    for model_values in models_values_list:
        treev_tree.insert('', tk.END, values=model_values)

    # Primary Button
    primary_button = tk.Button(buttons_frame, text="Primary Selected", command=lambda: primary_select_button(pri_win, treev_tree, models_submodels, match_model_name_var))
    primary_button.config( width = 15 )
    primary_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")
    # Close Button
    close_button = tk.Button(buttons_frame, text="Close", command=pri_win.destroy)
    close_button.config( width = 15 )
    close_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    pri_win.mainloop()
    return()

#############################
# Do Root Select Button
#############################
def do_root_select_button(root, show_folder_entry):
    global rgbeffects_file, show_folder
    logging.debug(f"show_folder: {show_folder_entry}")
    show_folder = show_folder_entry.replace("\\", "/")
    rgbeffects_file = show_folder + "/" + "xlights_rgbeffects.xml"
    logging.debug(f"show_folder: {show_folder}")
    # Verify xLights RGB Effects XML File Exists
    if os.path.isfile(rgbeffects_file):
        # Get Models subModel Dictionary from xlights rgbeffects_xml file
        models_submodels = get_models_submodels(rgbeffects_file)
        if (models_submodels is not None):
            for model, model_info in models_submodels.items():
                description = model_info.get("description", "")
                logging.debug("*" * 50)
                logging.debug(f"model: {model} {description}")
                logging.debug("*" * 50)
                submodels = model_info.get("submodels", [])
                for submodel in submodels:
                    logging.debug(f"+++ {submodel}")
            # Select Primary Model
            select_primary_model_window(root, rgbeffects_file, models_submodels)
        else:
            logging.error(f"No Models found in xLights RGB Effects Xml File {rgbeffects_file}")
            msgbox("Error:", f"No Models found in xLights RGB Effects XML File {rgbeffects_file}")
    else:
        logging.error(f"xLights RGB Effects XML File {rgbeffects_file} not found")
        msgbox("Error:", f"xLights RGB Effects XML File {rgbeffects_file} not found")
        rgbeffects_file = None

##################################
# Show Folder Window
##################################
def show_folder_window(show_folder):
    # 
    rgbeffects_file = None

    # Define Root Window
    root = tk.Tk()

    # Set Root Title
    root.title('Show Folder')

    # Set Window Width and Height
    w = 450 # width for map_win
    h = 100 # height for map_win

    # Calculate Window Cordinates
    (x, y) = calcxycoord(root, "west", w, h)
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # Set Style Theme
    style_s = ttk.Style()
    style_s.theme_use('clam')

    # Show Folder Label 
    show_folder_label = tk.Label(root, text="Show Folder:", justify=tk.RIGHT)
    show_folder_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

    # Show Folder Variable
    show_folder_var = tk.StringVar()
    show_folder_var.set(str(show_folder))

    # Show Folder Entry    
    show_folder_entry = tk.Entry(root, textvariable=show_folder_var, width=40, justify=tk.LEFT)
    show_folder_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

    # Show Folder Button
    root_select_button = tk.Button(root, text="Select Primary Model", command=lambda: do_root_select_button(root, show_folder_entry.get()))
    root_select_button.config( width = 20 )
    root_select_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    
    # Close Button
    root_close_button = tk.Button(root, text="Close", command=root.destroy)
    root_close_button.config( width = 15 )
    root_close_button.grid(row=1, column=1, padx=10, pady=10, sticky="w")
    #
    root.mainloop()
    return()

###############################
# main
###############################
def main():

    cli_parser = argparse.ArgumentParser(prog = 'map_models_submodels.py',
        description = '''%(prog)s is a tool to map a model/submodels to like model/submodels,''')
    
    ### Define Arguments
    cli_parser.add_argument('-l', '--logging_level', default = 30, type = int, choices = [0, 10, 20, 30, 40, 50], help = 'Logging Level',
        required = False)

    args = cli_parser.parse_args()
    
    logging_level = args.logging_level

    os_name = platform.system()
    logging.debug(f"Operating System: {os_name}")
    show_folder = ""
    # Windows OS?
    if (os_name == "Windows"):
        # Read the Xlights LastDir from HKEY_CURRENT_USER
        Xlights_last_dir = read_registry_value(winreg.HKEY_CURRENT_USER,
                                               "Software\\Xlights\\",
                                               "LastDir")
        if Xlights_last_dir:
            logging.debug(f"Xlights_last_dir: {Xlights_last_dir}")
            show_folder = Xlights_last_dir

    # Setup Logging
    setup_logging(logging_level)

    logging.info("#" * 50)
    logging.info("#" * 5 + " Map Model/Submodels Begin")
    logging.info("#" * 50)

    # Show Folder Window
    show_folder_window(show_folder)
    logging.info("#" * 50)
    logging.info("#" * 5 + " Map Model/Submodels End")
    logging.info("#" * 50)

if __name__ == "__main__":
    main()
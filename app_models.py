# This code is for checking and stopping the running models:
import os
import subprocess

def check_running_models(temp_folder: str):
    """Check the running models and save the output to a filename.

    Args:
        temp_folder (str): Temporary folder to store the temp text file

    Returns:
        str: Filename of the text file
    """

    filename = f"{temp_folder}/tmp_running_models.txt"

    # Clear the file if it already exists
    if os.path.exists(filename):
        os.remove(filename)

    # Run the command and save the output to the file
    subprocess.run(["ollama", "ps"], stdout=open(filename, "w"))

    return filename


def get_running_models(temp_folder: str):
    """Get the running models from the file as a list.
    
    Args:
        temp_folder (str): Temporary folder to store the temp text file

    Returns:
        list: List of running models
    """

    filename = check_running_models(temp_folder=temp_folder)
    running_models = []
    ind = 0

    with open(filename, "r") as file:
        for line_no, line_content in enumerate(file.readlines()):
            if line_no == 0:
                ind = line_content.find("ID")
            else:
                running_models.append(line_content[:ind].strip())

    return running_models


def stop_running_models(running_models: list):
    """Stop the running models.
    
    Args:
        running_models (list): List of running models
    """
    for model in running_models:
        subprocess.run(["ollama", "stop", model])
        


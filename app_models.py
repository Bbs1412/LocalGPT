# This code is for checking and stopping the running models:
import os
import subprocess

FOLDER = "Threads"
FILE = f"./{FOLDER}/tmp_running_models.txt"

if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

if os.path.exists(FILE):
    os.remove(FILE)


def check_running_models():
    """Check the running models and save the output to a file."""
    subprocess.run(["ollama", "ps"], stdout=open(FILE, "w"))


def get_running_models():
    """Get the running models from the file as a list."""
    check_running_models()
    running_models = []
    ind = 0

    with open(FILE, "r") as file:
        for line_no, line_content in enumerate(file.readlines()):
            if line_no == 0:
                ind = line_content.find("ID")
            else:
                running_models.append(line_content[:ind].strip())

    return running_models


def stop_running_models():
    """Stop the running models."""
    check_running_models()
    running_models = get_running_models()

    for model in running_models:
        subprocess.run(["ollama", "stop", model])

    os.remove(FILE)

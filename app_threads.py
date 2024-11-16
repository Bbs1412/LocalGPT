# This code handles the threads in the LocalGPT
# Image attachment are saved as the file paths in the json files
# Since thread is loaded form the file only once, base64s will be created and attached in the json->st.session_state.messages at that time
# But in rest (in the json saved), only the file paths will be saved
# Now, once thread with base64s is loaded in st, we do not load the json file again and again.
# Instead, st.session_state.messages (thread) is saved repeatedly in the json file
# So, while saving the thread, we will remove the base64s (file paths remain as it is since they were not updated / removed).


import os
import json
from datetime import datetime
from app_images import image_list_to_base64


def get_timestamp():
    """Get current timestamp in a formatted string

    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


# Get the time-stamp of the current time, suitable for filenames:
def get_timestamp_filename():
    """Get current timestamp in a formatted string, suitable for filenames

    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%d-%m-%Y_%H-%M-%S")


# Function to save conversation to a file:
def save_conversation(
        messages: list[dict],
        thread_name: str,
        model_name: str,
        thread_folder: str):
    """Save the conversation to a json file and update the config in same file with the last used model name

    Args:
        messages (list[dict]): List of messages to save
        thread_name (str): Name of the thread to save
        model_name (str): Name of the model used in the thread
        thread_folder (str): Folder where the thread is saved

    Returns:
        dict: Dictionary containing the status of the saving
    """
    ts = get_timestamp()

    try:
        # Remove the base64 images from the messages before saving to json
        for message in messages:
            if message.get("role") == "user" and "images" in message:
                del message["images"]

        json_to_save = {
            "config": {
                "model": model_name,
                "last_saved": ts
            },
            "messages": messages
        }

        filename = f"{thread_folder}/{thread_name}.json"
        with open(filename, "w") as file:
            json.dump(json_to_save, file, indent=4)

        return {"status": "success", "timestamp": ts}

    except Exception as e:
        return {"status": "error", "message": f"Failed to save thread. \n\n {str(e)}"}


# function to load conversation from a file:
def load_conversation(thread_name: str, thread_folder: str, image_folder: str):
    """Load the conversation from a json file and set the model to the last used model

    Args:
        thread_name (str): Name of the thread to load
        thread_folder (str): Folder where the thread is saved
        image_folder (str): Folder where the images are saved under threads' folders

    Returns:
        dict: Dictionary containing the messages, thread name, model name and last saved timestamp
    """

    try:
        filename = f"{thread_folder}/{thread_name}.json"

        with open(filename, "r") as file:
            thread_json = json.load(file)

        last_saved = thread_json.get("config", {}).get(
            "last_saved", get_timestamp())
        model_name = thread_json.get("config", {}).get("model", None)
        messages = thread_json.get("messages", [])

        # Add base64 images to the messages based on the image file paths:
        for message in messages:
            if message.get("role") == "user" and "image_files" in message:
                resp = image_list_to_base64(
                    image_list=message["image_files"],
                    image_folder=image_folder,
                    thread_name=thread_name
                )

                if resp["status"] == "success":
                    message["images"] = resp["result"]
                else:
                    # If there is error in processing some single image, return the error message of that image as it is
                    return resp

        return {
            "status": "success",
            "messages": messages,
            "thread_name": thread_name,
            "model_name": model_name,
            "last_saved": last_saved
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to load thread. \n\n {str(e)}"}


# Rename the thread file:
def rename_thread(
        old_thread_name: str,
        new_thread_name: str,
        thread_folder: str,
):
    """Rename the thread and its json file

    Args:
        old_thread_name (str): Old name of the thread
        new_thread_name (str): New name of the thread
        thread_folder (str): Folder where the thread is saved

    Returns:
        dict: Dictionary containing the status of the renaming
    """

    try:
        old_filename = f"{thread_folder}/{old_thread_name}.json"
        new_filename = f"{thread_folder}/{new_thread_name}.json"

        if os.path.exists(old_filename):
            os.rename(old_filename, new_filename)
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Thread not found"}

    except Exception as e:
        return {"status": "error", "message": f"Failed to rename thread. \n\n {str(e)}"}


# Load thread names by latest first order:
def load_thread_names(thread_folder: str):
    """Load all the thread names present in the Threads folder, based on the last modified time of the file

    Args:
        thread_folder (str): Folder where the threads are saved

    Returns:
        list: List of thread names
    """

    thread_names = []
    files = []
    for file in os.listdir(thread_folder):
        if file.endswith(".json"):
            files.append(file)

    files.sort(key=lambda x: os.path.getmtime(
        f"{thread_folder}/{x}"), reverse=True)

    for file in files:
        thread_names.append(file.split(".")[0])

    return thread_names


# Delete the thread:
def delete_thread(
        thread_name: str,
        thread_folder: str,
        deleted_threads_folder: str,
        image_folder: str,
        deleted_images_folder: str
        ):
    """Deletes the thread from page view, but actually moves it to 'deleted' folder

    Args:
        thread_name (str): Name of the thread to delete
        thread_folder (str): Folder where the thread is saved
        deleted_threads_folder (str): Folder where the deleted threads are moved
        image_folder (str): Folder where the images are saved under threads' folders
        deleted_images_folder (str): Folder where the deleted images are moved

    Returns:
        dict: Dictionary containing the status of the deletion
    """

    try:
        old_filename = f"{thread_folder}/{thread_name}.json"
        new_filename = f"{deleted_threads_folder}/{thread_name}.json"

        # If file already exists in deleted folder, add timestamp to new filename:
        if os.path.exists(new_filename):
            new_filename = f"{deleted_threads_folder}/{thread_name}_{get_timestamp_filename()}.json"

        # Move the file to deleted folder
        if os.path.exists(old_filename):
            os.rename(old_filename, new_filename)

        # Move the thread's images folder to deleted folder:
        old_image_folder = f"{image_folder}/{thread_name}"
        new_image_folder = f"{deleted_images_folder}/{thread_name}/"

        if not os.path.exists(new_image_folder):
            os.makedirs(new_image_folder)

        if os.path.exists(old_image_folder):
            for file in os.listdir(old_image_folder):
                os.rename(f"{old_image_folder}/{file}", f"{new_image_folder}/{file}")

            os.rmdir(old_image_folder)

        return {"status": "success"}

    except Exception as e:
        return {"status": "error", "message": f"Failed to delete thread. \n\n {str(e)}"}
    
        
# ---------------------------------------------------------------------------------------
# Test calls:
# ---------------------------------------------------------------------------------------

# # Save conversation:
# messages = [
#     {
#         "role": "ai",
#                 "content": "Hello 👋, How may I help you?"
#     },
#     {
#         "role": "user",
#                 "content": "prompt",
#                 "image_files": ["filename.png"],
#                 "images": ["this base64 should be removed"]
#     }
# ]

# save_conversation(
#     messages=messages,
#     thread_name="test_save_thread",
#     model_name="bs3.1:latest",
#     folder="Threads"
# )


# # Load conversation:
# conversation = load_conversation(
#     thread_name="test_save_thread",
#     thread_folder="Threads",
#     image_folder="Threads/images"
# )

# print(json.dumps(conversation, indent=4))

# # Rename thread:
# a = rename_thread(
#     old_thread_name="test_save_thread_renamed",
#     new_thread_name="test_save_thread",
#     thread_folder="Threads"
# )

# print(json.dumps(a, indent=4))

# # Load thread names:
# thread_names = load_thread_names("Threads")
# print(thread_names)


# # Delete thread:
# a = delete_thread(
#     thread_name="test_save_thread",
#     thread_folder="Threads",
#     deleted_threads_folder="Threads/deleted",
#     image_folder="Threads/images",
#     deleted_images_folder="Threads/deleted/images"
# )
# print(json.dumps(a, indent=4))

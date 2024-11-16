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


def get_timestamp():
    """Get current timestamp in a formatted string

    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


#

# Function to save conversation to a file:
def save_conversation(messages: list[dict], thread_name: str, model_name: str, folder: str):
    """Save the conversation to a json file and update the config in same file with the last used model name
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
                "last_updated": ts
            },
            "messages": messages
        }

        filename = f"{folder}/{thread_name}.json"
        with open(filename, "w") as file:
            json.dump(json_to_save, file, indent=4)

        return {"status": "success", "timestamp": ts}

    except Exception as e:
        return {"status": "error", "message": f"Failed to save thread. \n\n {str(e)}"}


# # function to load conversation from a file:
# def load_conversation(thread_name: str = "conversation_history"):
#     """Load the conversation from a json file and set the model to the last used model

#     Args:
#         filename (str, optional): Filename to load the conversation. Defaults to "conversation_history.json".
#     """
#     filename = f"{st.session_state.thread_folder}/{thread_name}.json"
#     with open(filename, "r") as file:
#         st.session_state.messages = json.load(file)

#     # Set the thread name from the filename
#     st.session_state.thread_name = thread_name

#     # Get the last modified time of the file (this will be the last saved timestamp)
#     last_modified_time = os.path.getmtime(filename)
#     st.session_state.last_saved = datetime.fromtimestamp(
#         last_modified_time).strftime("%Y-%m-%d %H:%M:%S")

#     # Load the last used model as well:
#     config_path = f"{st.session_state.thread_folder}/{st.session_state.config_file}"
#     with open(config_path, 'r') as file:
#         config = json.load(file)

#     if thread_name not in config:
#         st.session_state.model = st.session_state.default_model
#     else:
#         st.session_state.model = config[thread_name]

# # Rename the thread file:


# def rename_thread(new_name: str):
#     """Rename the thread and its json file

#     Args:
#         new_name (str): New name for the thread and json file
#     """
#     old_filename = f"{st.session_state.thread_folder}/{st.session_state.thread_name}.json"
#     new_filename = f"{st.session_state.thread_folder}/{new_name}.json"

#     if os.path.exists(old_filename):
#         os.rename(old_filename, new_filename)

#     st.session_state.thread_name = new_name
#     save_conversation(f"{st.session_state.thread_folder}/{new_name}.json")
#     st.toast("Thread renamed successfully!",
#              icon=st.session_state.icons['rename_thread'])


# # Load thread names by latest first order:
# def load_thread_names():
#     """Load all the thread names present in the Threads folder, based on the last modified time of the file

#     Returns:
#         list: List of thread names
#     """
#     thread_names = []
#     files = []
#     for file in os.listdir(st.session_state.thread_folder):
#         if file.endswith(".json"):
#             if file != st.session_state.config_file:
#                 files.append(file)

#     files.sort(key=lambda x: os.path.getmtime(
#         f"{st.session_state.thread_folder}/{x}"), reverse=True)

#     for file in files:
#         thread_names.append(file.split(".")[0])

#     return thread_names


# # Delete the thread:
# def delete_thread(thread_name: str):
#     """Deletes the thread from page view, but actually moves it to 'deleted' folder

#     Args:
#         thread_name (str): Name of the thread to delete
#     """

#     old_filename = f"{st.session_state.thread_folder}/{thread_name}.json"
#     new_filename = f"{st.session_state.thread_folder}/deleted/{thread_name}.json"

#     # Create deleted folder if not exists
#     if not os.path.exists(f"{st.session_state.thread_folder}/deleted"):
#         os.makedirs(f"{st.session_state.thread_folder}/deleted")

#     # If file already exists in deleted folder, add timestamp to new filename:
#     if os.path.exists(new_filename):
#         new_filename = f"{st.session_state.thread_folder}/deleted/{thread_name}_{get_timestamp_filename()}.json"

#     # Move the file to deleted folder
#     if os.path.exists(old_filename):
#         os.rename(old_filename, new_filename)

#     st.session_state.thread_name = "New Thread"
#     st.session_state.pop('messages')
#     # st.rerun()

#     st.toast(f"Thread `{thread_name}` deleted successfully!",
#              icon=st.session_state.icons['delete_thread'])

# ---------------------------------------------------------------------------------------
# Test calls:
# ---------------------------------------------------------------------------------------

# Save conversation:
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

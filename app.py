# streamlit basic code:
import os
import json
import base64
import ollama
import app_images
import app_models
import streamlit as st
from time import sleep
from typing import Literal
from datetime import datetime

# ---------------------------------------------------------------------------------------
# Config and Sidebar:
# ---------------------------------------------------------------------------------------

if 'thread_name' not in st.session_state:
    # a = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # st.session_state.thread_name = f"New Thread {a}"
    st.session_state.thread_name = f"New Thread"

st.set_page_config(
    page_title=f"GenAI Assistant : {st.session_state.thread_name}",
    page_icon="🤖",
    layout='centered',
    initial_sidebar_state='expanded',
    menu_items={
        'About': "# This is a simple chatbot app using Streamlit",
    }
)

st.logo("./assets/infinity.ico")

# ---------------------------------------------------------------------------------------
# Session State:
# ---------------------------------------------------------------------------------------

if 'icons' not in st.session_state:
    st.session_state.icons = {
        # 'ai' : "ai" or "🤖" or "https://upload.wikimedia.org/wikipedia/commons/0/04/ChatGPT_logo.svg",
        'ai': "./assets/icon_ai.svg",

        # 'user' : "user" or "🕵️" or "./assets/icon_user.png",
        'user': "./assets/icon_user.png",

        # 'delete_thread' : "🗑️" or "./assets/icon_delete_chat.svg",
        'delete_thread': "🗑️",

        'rename_thread': "🎫",
    }

if 'debug' not in st.session_state:
    st.session_state.debug = True

if 'default_model' not in st.session_state:
    st.session_state.default_model = "llama3.1:latest"

if 'model' not in st.session_state:
    # st.session_state.model = "codellama:latest"
    st.session_state.model = st.session_state.default_model

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": 'ai',
        "content": "Hello 👋, How may I help you?"
    }]

if 'last_saved' not in st.session_state:
    st.session_state.last_saved = None

if 'thread_folder' not in st.session_state:
    st.session_state.thread_folder = "./Threads"

if 'config_file' not in st.session_state:
    # ./threads/config.json
    st.session_state.config_file = f"_configs.json"

if 'info' not in st.session_state:
    st.session_state.info = {}
    with open("assets/app_features.md", "r") as file:
        st.session_state.info['features'] = file.read()
    with open("assets/app_help.md", "r") as file:
        st.session_state.info['help'] = file.read()

if "temp_cleared" not in st.session_state:
    app_images.clear_temp_images()
    st.session_state.temp_cleared = True

# ---------------------------------------------------------------------------------------
# Functions:
# ---------------------------------------------------------------------------------------

# Get the time-stamp of the current time:


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


def write_as_ai(message: str):
    """Makes a new entry in the thread with role of AI

    Args:
        message (string): Content to write into that entry
    """
    with st.chat_message("ai", avatar=st.session_state.icons['ai']):
        st.markdown(message['content'])


def write_as_user(message: str):
    """Makes a new entry in the thread with role of User

    Args:
        message (string): Content to write into that entry
    """
    with st.chat_message("user", avatar=st.session_state.icons['user']):
        st.write(message['content'])
        # if there are images, then show them as well
        if 'images' in message:
            # if there are multiple, make the n columns and show them
            col_list = st.columns(len(message['images']))

            # for i in range(cnt):
            for i, (img, mime) in enumerate(zip(message['images'], message['mimes'])):
                resp = app_images.get_image_from_b64(img, mime)

                if resp['status'] == 'error':
                    st.error(
                        f"Error: Some error occurred while showing the image: {resp['message']}")
                else:
                    col_list[i].image(resp['path'], use_column_width=True)
                    # st.image(resp['path'], width=150)


why = """
    This create_message function is needed as, when model is yielding live response, we can write it only by the write_stream function, because it supports live read and write simultaneously.
    As building logic to constantly update the response parts in st session state messages is not feasible, so, live response is passed directly to that UI function, it will keep on updating the response and,
    Later, once the response is fully received, it will be saved in messages in st session state and then we can write_as_ai using our normal functions once we have it.
"""


def create_message(role: Literal['user', 'ai'], content: str):
    """Creates a new message and appends it to the thread

    Args:
        role (Literal['user', 'ai']): Role of the message (User or AI)
        content (str): Content of the message
    """
    # new_msg = {"role": role, "content": content}
    # st.session_state.messages.append(new_msg)

    # Check for images in the user's prompt content:
    # +++{image: ["path/to/image.jpg", "image2.png"]}+++
    if role == 'user':
        has_image = app_images.check_if_image_in_prompt(content)
        if has_image:
            # Extract the images from the prompt:
            contents = app_images.parse_images_from_prompt(content)

            if contents['status'] == 'error':
                st.error(
                    f"Error: Error in separating the prompt and images from the input")
                st.error(f"Error: {contents['message']}")
                return

            else:
                # Convert the image paths to base64:
                b64_img_list = app_images.image_list_to_base64(
                    contents['image_list'])

                if b64_img_list['status'] == 'error':
                    st.error(
                        f"Error: {b64_img_list['message']} for `{b64_img_list['path']}`")
                    return

                new_msg = {
                    "role": role,
                    "content": contents['prompt'],
                    "images": b64_img_list['result'],
                    "mimes": b64_img_list['mime_types']
                }

        else:
            new_msg = {"role": role, "content": content}

    else:
        new_msg = {"role": role, "content": content}

    st.session_state.messages.append(new_msg)

    if role == 'ai':
        write_as_ai(new_msg)
    else:
        write_as_user(new_msg)


# Function to get response from the chatbot model:
def get_response(full_response: bool = False):
    """Get response from the chatbot model

    Args:
        full_response (bool, optional): If True, returns full response at once. Defaults to False.

    Yields:
        str: Response from the large language model.
    """
    response = ollama.chat(
        model=st.session_state['model'],
        messages=st.session_state['messages'],
        stream=True,
        # format='json',
        format='',
    )

    # Return is one time statement, but yield is a generator
    if full_response:
        return response
    # It returns one iterator, and then waits for the next response(s) to come
    # New responses keep on coming, and we can keep on yielding them using that iterator
    for chunk in response:
        yield chunk["message"]["content"]


def update_config_file(thread_name, model_name):
    """Update the config file with the latest model and thread name

    Args:
        thread_name (str): Name of the thread
        model_name (str): Name of the model
    """
    # update the config file with the latest model and thread name:
    config_path = f"{st.session_state.thread_folder}/{st.session_state.config_file}"

    # Step 1: Read the existing config file
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty config dictionary
        config = {}

    # Step 2: Update the config dictionary with the latest model and thread name
    config[thread_name] = model_name

    # Step 3: Write the updated config dictionary back to the file
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)


# Function to save conversation to a file:
def save_conversation(filename: str = "conversation_history.json"):
    """Save the conversation to a json file and update the config file with the latest model and thread name

    Args:
        filename (str, optional): Filename to save the conversation. Defaults to "conversation_history.json".
    """
    if not os.path.exists(st.session_state.thread_folder):
        os.makedirs(st.session_state.thread_folder)

    with open(filename, "w") as file:
        json.dump(st.session_state.messages, file, indent=4)

    st.session_state.last_saved = get_timestamp()
    # st.toast("Conversation saved successfully!", icon="📝")

    update_config_file(st.session_state.thread_name, st.session_state.model)


# function to load conversation from a file:
def load_conversation(thread_name: str = "conversation_history"):
    """Load the conversation from a json file and set the model to the last used model

    Args:
        filename (str, optional): Filename to load the conversation. Defaults to "conversation_history.json".
    """
    filename = f"{st.session_state.thread_folder}/{thread_name}.json"
    with open(filename, "r") as file:
        st.session_state.messages = json.load(file)

    # Set the thread name from the filename
    st.session_state.thread_name = thread_name

    # Get the last modified time of the file (this will be the last saved timestamp)
    last_modified_time = os.path.getmtime(filename)
    st.session_state.last_saved = datetime.fromtimestamp(
        last_modified_time).strftime("%Y-%m-%d %H:%M:%S")

    # Load the last used model as well:
    config_path = f"{st.session_state.thread_folder}/{st.session_state.config_file}"
    with open(config_path, 'r') as file:
        config = json.load(file)

    if thread_name not in config:
        st.session_state.model = st.session_state.default_model
    else:
        st.session_state.model = config[thread_name]

# Rename the thread file:


def rename_thread(new_name: str):
    """Rename the thread and its json file

    Args:
        new_name (str): New name for the thread and json file
    """
    old_filename = f"{st.session_state.thread_folder}/{st.session_state.thread_name}.json"
    new_filename = f"{st.session_state.thread_folder}/{new_name}.json"

    if os.path.exists(old_filename):
        os.rename(old_filename, new_filename)

    st.session_state.thread_name = new_name
    save_conversation(f"{st.session_state.thread_folder}/{new_name}.json")
    st.toast("Thread renamed successfully!",
             icon=st.session_state.icons['rename_thread'])


# Load thread names by latest first order:
def load_thread_names():
    """Load all the thread names present in the Threads folder, based on the last modified time of the file

    Returns:
        list: List of thread names
    """
    thread_names = []
    files = []
    for file in os.listdir(st.session_state.thread_folder):
        if file.endswith(".json"):
            if file != st.session_state.config_file:
                files.append(file)

    files.sort(key=lambda x: os.path.getmtime(
        f"{st.session_state.thread_folder}/{x}"), reverse=True)

    for file in files:
        thread_names.append(file.split(".")[0])

    return thread_names


# Delete the thread:
def delete_thread(thread_name: str):
    """Deletes the thread from page view, but actually moves it to 'deleted' folder

    Args:
        thread_name (str): Name of the thread to delete
    """

    old_filename = f"{st.session_state.thread_folder}/{thread_name}.json"
    new_filename = f"{st.session_state.thread_folder}/deleted/{thread_name}.json"

    # Create deleted folder if not exists
    if not os.path.exists(f"{st.session_state.thread_folder}/deleted"):
        os.makedirs(f"{st.session_state.thread_folder}/deleted")

    # If file already exists in deleted folder, add timestamp to new filename:
    if os.path.exists(new_filename):
        new_filename = f"{st.session_state.thread_folder}/deleted/{thread_name}_{get_timestamp_filename()}.json"

    # Move the file to deleted folder
    if os.path.exists(old_filename):
        os.rename(old_filename, new_filename)

    st.session_state.thread_name = "New Thread"
    st.session_state.pop('messages')
    # st.rerun()

    st.toast(f"Thread `{thread_name}` deleted successfully!",
             icon=st.session_state.icons['delete_thread'])


# ---------------------------------------------------------------------------------------
# Sidebar Actions:
# ---------------------------------------------------------------------------------------


st.sidebar.title(":gear: :orange[Customize here:] ")
# st.sidebar.markdown("---")


# Load Model:
available_models = []
all_models = ollama.list()["models"]
actual_names = [model['name'] for model in all_models]


def model_mapper(model_name: str):
    """Maps the modified model name to the actual name used by Ollama"""
    ind = available_models.index(model_name)
    return actual_names[ind]


# Choose form available models:
for model in ollama.list()["models"]:
    model_family = model['details']['family'].ljust(8)
    model_parameters = model['details']['parameter_size'].rjust(8)
    model_name = model['name']
    # available_models.append(f'{model_family}{model_parameters} : {model_name}')
    available_models.append(f'{model_name} {model_parameters}')


# st.write(model_mapper(available_models[4]))
selected_model = st.sidebar.selectbox(
    label="Choose Model:",
    options=available_models,
    help="Choose the model you want to use for the chatbot. Figures on the right are model parameter size",
    index=actual_names.index(st.session_state.model)
)
st.session_state.model = model_mapper(selected_model)
# st.write(st.session_state.model)


# st.sidebar.markdown("---")

ex = st.sidebar.expander("Features of App:")
ex.write(st.session_state.info['features'])

st.sidebar.markdown("---")

st.sidebar.header(":red[Chat Archives:]")

cont = st.sidebar.container(border=True)
a, b, c = cont.columns([8.5, 1.25, 0.5], vertical_alignment='top')
a.header(":green[Current Thread:]")
btn = b.button("✍️", type='secondary', help="Create a new thread")

if btn:
    a = get_timestamp()
    # st.session_state.thread_name = f"New Thread {a}"
    st.session_state.thread_name = f"New Thread"
    st.session_state.pop('messages')
    st.rerun()


# Thread Name Input (Editable):
new_thread_name = cont.text_input(
    label="Edit Thread Name:",
    value=st.session_state.thread_name,
    help="Rename the thread."
)

# Rename thread file if name changed
if new_thread_name != st.session_state.thread_name:
    rename_thread(new_thread_name)

# Show last saved timestamp (below thread name)
if st.session_state.last_saved:
    cont.caption(f"Last saved: {st.session_state.last_saved}")


# load all the saved thread names using files:
threads = load_thread_names()

# thread_buttons, thread_deletes = st.sidebar.columns([.85, .15])
thread_buttons, thread_deletes = st.sidebar.columns([.95, .05], gap='small')

# Create buttons for each thread, and load the conversation when clicked
# Also disable the button if it is already selected
threads_btn = []
threads_dlt = []
for ind, i in enumerate(threads):
    threads_btn.append(
        # st.sidebar.button(
        thread_buttons.button(
            label=i,
            key=f't_{i}',
            use_container_width=True,
            on_click=lambda i=i: load_conversation(i),
            disabled=True if i == st.session_state.thread_name else False
        )
    )

    threads_dlt.append(
        thread_deletes.button(
            label="×",
            key=f'del_{i}',
            type='secondary',
            use_container_width=True,
            on_click=lambda i=i: delete_thread(i),
        )
    )

# ---------------------------------------------------------------------------------------
# Running Models Section:
# ---------------------------------------------------------------------------------------

st.sidebar.markdown("---")
models_sec = st.sidebar.expander("Running Models:", expanded=False)

col1, col2 = models_sec.columns(2)

if col1.button("Check Models"):
    running_model_names = app_models.get_running_models()
    models_sec.write(running_model_names)

if col2.button("Stop Models"):
    app_models.stop_running_models()
    models_sec.success("Stopped all running models.")


# ---------------------------------------------------------------------------------------
# Help Guide:
# ---------------------------------------------------------------------------------------

st.sidebar.markdown("---")

st.sidebar.header(":red[Help Section:]")

# Enable / Disable Debugging:
st.session_state.debug = st.sidebar.checkbox(
    label="Debug Mode",
    value=False,
    key='debug2',
    help='Shows internal pointer variables 😂. (Shows the json file on page)'
)

dabba = st.sidebar.container(border=True)
dabba.markdown(st.session_state.info['help'])


# ---------------------------------------------------------------------------------------
# Take new input from user:
# ---------------------------------------------------------------------------------------

st.subheader(
    f'✨:blue[MyGPT Local :]  {st.session_state.thread_name}', divider='rainbow')


# Write olf messages on every rerun
for message in st.session_state.messages:
    if message['role'] == 'ai':
        write_as_ai(message)
    else:
        write_as_user(message)


if inp := st.chat_input('Type your message / prompt here... [Attachments are also supported!!!]'):
    # If there are image attachments, then, need to handle them separately.
    # Implemented it in create_message function...
    create_message('user', inp)

    try:
        # temp_container = st.container(border=True)
        # response_text = temp_container.write_stream(get_response())

        temp_container = st.container(border=True)
        logo_width = 0.6
        a, b = temp_container.columns([logo_width, 10-logo_width])
        a.image(st.session_state.icons['ai'])
        response_text = b.write_stream(get_response())

        # Store the full response, so in next run of the st app, we can display the full response in the chat (automatically)
        if inp:
            create_message('ai', response_text)
            st.rerun()

    except Exception as e:
        st.write(e)

    finally:
        save_conversation(
            f"{st.session_state.thread_folder}/{st.session_state.thread_name}.json")


# ---------------------------------------------------------------------------------------
# Upload File as System Prompt:
# [ https://discuss.streamlit.io/t/how-do-i-replicate-chatgpt-file-upload-option-ui/51781/6 ]
# ---------------------------------------------------------------------------------------
# import time
# chat_box = st.chat_input("What do you want to do?")

# if "uploader_visible" not in st.session_state:
#     st.session_state["uploader_visible"] = False
# def show_upload(state:bool):
#     st.session_state["uploader_visible"] = state

# with st.chat_message("system"):
#     cols= st.columns((3,1,1))
#     cols[0].write("Do you want to upload a file?")
#     cols[1].button("yes", use_container_width=True, on_click=show_upload, args=[True])
#     cols[2].button("no", use_container_width=True, on_click=show_upload, args=[False])


# if st.session_state["uploader_visible"]:
#     with st.chat_message("system"):
#         file = st.file_uploader("Upload your data")
#         if file:
#             with st.spinner("Processing your file"):
#                 time.sleep(5) #<- dummy wait for demo.


# ---------------------------------------------------------------------------------------
# Debugging:
# ---------------------------------------------------------------------------------------

if st.session_state.debug:
    ex = st.expander("Debugging")
    ex.write(st.session_state.messages)

# streamlit basic code:
import os
import json
import ollama
import app_models
import app_images
import app_threads
from time import sleep
import streamlit as st
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

        # 'save_thread': "💾" or "✅"
        'save_thread': "✅",
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

if 'folder' not in st.session_state:
    st.session_state.folder = {
        'threads': "./Threads",
        'deleted': "./Threads/deleted",
        'images': "./Threads/images",
        'temp': "./Threads/temp"
    }

    # Create the folders if they don't exist:
    for folders in st.session_state.folder.values():
        if not os.path.exists(folders):
            os.makedirs(folders)

if 'config_file' not in st.session_state:
    # ./threads/config.json
    st.session_state.config_file = f"_configs.json"

if 'info' not in st.session_state:
    st.session_state.info = {}
    with open("assets/app_features.md", "r") as file:
        st.session_state.info['features'] = file.read()
    with open("assets/app_help.md", "r") as file:
        st.session_state.info['help'] = file.read()

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


# ---------------------------------------------------------------------------------------
# Thread Functions:
# ---------------------------------------------------------------------------------------
def load_conversation_helper_fn(thread_name:str):
    """Helper function to load the conversation of the selected thread

    Args:
        thread_name (str): Name of the thread to load
    """
    # Load the conversation from the thread:
    resp = app_threads.load_conversation(
        thread_name=thread_name,
        thread_folder=st.session_state.folder['threads']
        image_folder=st.session_state.folder['images']
    )

    if resp['status'] == 'error':
        # There might be some error in image conversion here, or thread loading (json) can go wrong, all errors are handled here dynamically
        st.error(f"Error: {resp['message']}")
    else:
        st.session_state.messages = resp['messages']
        st.session_state.thread_name = resp['thread_name']
        st.session_state.model = resp['model_name']
        st.session_state.last_saved = resp['last_saved']
        st.rerun()

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
            on_click=lambda i=i: load_conversation_helper_fn(i),
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
        resp = app_threads.save_conversation(
            messages=st.session_state.messages,
            thread_name=st.session_state.thread_name,
            model_name=st.session_state.model,
            thread_folder=st.session_state.folder['threads']
        )

        if resp['status'] == 'error':
            st.error(f"Error: {resp['message']}")
        else:
            st.session_state.last_saved = resp['timestamp']

            st.toast("Conversation saved successfully!",
                     icon=st.session_state.icons['save_thread'])


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

import os
import base64
import shutil
from datetime import datetime


def get_timestamp():
    """Get current timestamp in a formatted string

    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime("%d-%m-%Y %H-%M-%S")


def check_if_image_in_prompt(prompt: str):
    """ Checks if the prompt contains an image

    Args:
        prompt (str): The prompt of user input

    Returns:
        bool: True if image is present, False otherwise
    """
    if prompt.find("+++{image:") != -1:
        return True
    else:
        return False


def parse_images_from_prompt(prompt: str):
    """Extracts the image paths from the prompt

    Args:
        prompt (str): The prompt containing the image paths

    Returns:
        list: List of image paths
    """

    start_ind = prompt.find("+++{image:")
    end_ind = prompt.find("}+++")

    if start_ind != -1 and end_ind != -1:
        imp = prompt[start_ind+10: end_ind].strip()

        # Replace the \ in the path with \\, so that it can be evaluated as a string
        # "E:\Projects\Local ChatGPT\assets\icon_user.png"
        # This is looking normal string, but when we evaluate it, it will be treated as escape sequence at some places like \P, \L, \a, etc.
        # So, we need to escape the \ ( \ -> \\ ) so that it can be evaluated as a string
        imp = imp.replace("\\", "\\\\")
        imp = eval(imp)

        # If it is single image, then convert it to list:
        if not isinstance(imp, list):
            image_list = [imp]
        # Else, it is already a list due to eval function
        else:
            image_list = imp

        prompt = prompt[:start_ind] + prompt[end_ind+4:]
        return {"status": "success", "image_list": image_list, "prompt": prompt}
    else:
        return {"status": "error", "message": "Some error occurred while parsing the images"}


def save_images_locally(image_list: list, image_folder: str, thread_name: str):
    """Saves the images locally in the specified thread folder from the list of image paths (passed by user from anywhere in the system)

    Args:
        image_list (list): List of image paths
        image_folder (str): Image folder path under which the images are to be stored
        thread_name (str): Name of the thread (to create subfolder under image_folder)

    Returns:
        dict: Dictionary containing the status and path of the saved images
    """

    # Create the thread folder if it does not exist
    thread_images_folder = os.path.join(image_folder, thread_name)
    os.makedirs(thread_images_folder, exist_ok=True)

    error_flag = False
    error_log = ""
    error_path = ""

    local_image_list = []
    for image_path in image_list:
        try:
            # Validate the image path exists
            if not os.path.exists(image_path):
                error_flag = True
                error_log = f"Error: Image not found at path: {image_path}"
                error_path = image_path
                break

            # Copy the image to the thread folder
            # old_image_path = image_path
            # new_image_path = f"{image_folder}/{thread_name}/{os.path.basename(image_path)}"
            base_name = os.path.basename(image_path)
            new_image_path = os.path.join(thread_images_folder, base_name)

            # Append timestamp if the file already exists
            if os.path.exists(new_image_path):
                timestamp = get_timestamp()
                name, ext = os.path.splitext(base_name)
                new_image_path = os.path.join(
                    thread_images_folder, f"{name}_{timestamp}{ext}")

            # Copy the file to the new path
            shutil.copy(image_path, new_image_path)
            local_image_list.append(os.path.basename(new_image_path))

        except Exception as e:
            error_flag = True
            error_log += f"Error: {e}"
            error_path = image_path
            break

    if error_flag:
        return {"status": "error", "message": error_log, "path": error_path}
    else:
        return {"status": "success", "image_list": local_image_list}


def path_to_base64(image_path: str):
    """Converts the image at the path to base64 format

    Args:
        path (str): Path of the image file

    Returns:
        str: Base64 encoded image
    """

    try:
        # Open the file in binary mode
        with open(image_path, "rb") as image_file:
            # Encode the image file to base64
            encoded_string = base64.b64encode(
                image_file.read()).decode('utf-8')

        # Determine the MIME type based on file extension
        mime_type = image_path.split('.')[-1].lower()
        if mime_type not in ["png", "jpg", "jpeg", "gif", "bmp", "webp"]:
            raise ValueError("Unsupported image format")

        return {"status": "success", "result": encoded_string, "mime_type": mime_type}

    except Exception as e:
        return {'status': "error", "message": f"Error: {e}", "path": image_path}


def image_list_to_base64(image_list: list, image_folder: str, thread_name: str):
    """Converts the list of image paths to base64 format

    Args:
        image_list (list): List of image paths
        image_folder (str): Path of Folder containing the images
        thread_name (str): Name of the thread

    Returns:
        dict: Dictionary containing the status and base64 encoded images
    """

    base64_images = []
    mimes = []
    error_flag = False
    error_log = ""
    error_path = ""

    for image_path in image_list:
        # image is stored in: Threads/images/thread_name/image_name
        # Because, in case of thread deletion, we can delete the whole image folder of that thread
        image_path = f"{image_folder}/{thread_name}/{image_path}"
        result = path_to_base64(image_path)

        if result['status'] == 'error':
            error_flag = True
            error_log += f"Error: {result['message']}"
            error_path = result['path']
            break

        else:
            base64_images.append(result['result'])
            mimes.append(result['mime_type'])

    # Return the failure of processing single image as failure of processing entire list of images!!! The error of that particular image is returned as it is:
    if error_flag:
        return {"status": "error", "message": error_log, "path": error_path}
    else:
        return {"status": "success", "result": base64_images, "mime_types": mimes}


# def get_image_from_b64(base64_string: str, mime: str):
#     """ Get the image from the base64 string

#     Args:
#         base64_string (str): Base64 encoded image
#         mime (str): MIME type of the image

#     Returns:
#         dict: Dictionary containing the status and path of the saved image
#     """

#     # create temp_images directory if it does not exist
#     if not os.path.exists("temp_images"):
#         os.makedirs("temp_images")

#     # generate a random path to save the image
#     save_path = f"temp_images/{get_timestamp()}.{mime}"

#     try:
#         # Decode the base64 string
#         decoded_image = base64.b64decode(base64_string)

#         # Save the image to the specified path
#         with open(save_path, "wb") as image_file:
#             image_file.write(decoded_image)

#         return {"status": "success", "path": save_path}

#     except Exception as e:
#         return {"status": "error", "message": f"Error: {e}"}


# def clear_temp_images():
#     """Clears the temp_images directory"""

#     for file in os.listdir("temp_images"):
#         file_path = os.path.join("temp_images", file)
#         try:
#             if os.path.isfile(file_path):
#                 os.unlink(file_path)
#         except Exception as e:
#             print(f"Error: {e}")
#     print("Temp images cleared")

# print(get_image_from_b64("sdsdf"))

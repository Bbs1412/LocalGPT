import os
import base64
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
        # if mime_type not in ["png", "jpg", "jpeg", "gif", "bmp", "webp"]:
        #     raise ValueError("Unsupported image format")

        # Return as a data URI
        # return f"data:image/{mime_type};base64,{encoded_string}"
        return {"status": "success", "result": encoded_string, "mime_type": mime_type}

    except Exception as e:
        return {'status': "error", "message": f"Error: {e}", "path": image_path}


def image_list_to_base64(image_list: list):
    """Converts the list of image paths to base64 format

    Args:
        image_list (list): List of image paths

    Returns:
        list: List of base64 encoded images
    """

    base64_images = []
    mime_types = []
    for image_path in image_list:
        result = path_to_base64(image_path)

        if result['status'] == 'error':
            return {"status": "error", "result": result['message'], "path": result['path']}

        else:
            base64_images.append(result['result'])
            mime_types.append(result['mime_type'])

    return {"status": "success", "result": base64_images, "mime_types": mime_types}


def get_image_from_b64(base64_string: str, mime: str):
    """ Get the image from the base64 string

    Args:
        base64_string (str): Base64 encoded image
        mime (str): MIME type of the image

    Returns:
        dict: Dictionary containing the status and path of the saved image
    """

    # create temp_images directory if it does not exist
    if not os.path.exists("temp_images"):
        os.makedirs("temp_images")

    # generate a random path to save the image
    save_path = f"temp_images/{get_timestamp()}.{mime}"

    try:
        # Decode the base64 string
        decoded_image = base64.b64decode(base64_string)

        # Save the image to the specified path
        with open(save_path, "wb") as image_file:
            image_file.write(decoded_image)

        return {"status": "success", "path": save_path}

    except Exception as e:
        return {"status": "error", "message": f"Error: {e}"}


def clear_temp_images():
    """Clears the temp_images directory"""

    for file in os.listdir("temp_images"):
        file_path = os.path.join("temp_images", file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error: {e}")
    print("Temp images cleared")

# print(get_image_from_b64("sdsdf"))

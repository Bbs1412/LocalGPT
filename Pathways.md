# Development Pathways:

## Iteration 1 (23/10/2024):
- Making a good UI to interact with LLMs

## Iteration 2 (24/10/2024):
- Adding a feature to save the model and load it later

## Iteration 3 (25/10/2024):
- Loading the thread names based on their modification datetime

## Iteration 4 (25/10/2024):
- Delete threads using button

## Iteration 5 (26/10/2024):
- Feature to save the last used LLM with the thread
- Open it automatically with that thread...

## Iteration 6 (16/11/2024):
- Changed UI
- Added feature to Check and Stop Running Models
- Added Modularity to the code
- Added Image Support (LLama vision and Llava)

## Iteration 7 (17/11/2024):
- Completely modularized the threads codes
- Refactored the image logic Completely

## Iteration 8 (04/01/2024):
- Save the images in local file, store new name (path) in thread json
- Make the subprocess to copy the parsed image to the local folder

## Iteration 9 (05/01/2024):
- Updated requirements
- Fixed compatibility with latest versions of ollama and streamlit

--- 

# Future plans:
- try except in the write_stream to save the half response at least in case of error
- Update the docstring-s of functions in the app_threads file
- Move the LLM model sidebar out of app.py
- Integrate lang-chain in it


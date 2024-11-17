# LocalGPT
Clone of ChatGPT to get same functionality using open source LLMs offline, locally.

---

# Iteration 1 (23/10/2024):
Making a good UI to interact with LLMs

# Iteration 2 (24/10/2024):
Adding a feature to save the model and load it later

# Iteration 3 (25/10/2024):
Loading the thread names based on their modification datetime

# Iteration 4 (25/10/2024):
Delete threads using button

# Iteration 5 (26/10/2024):
Feature to save the last used LLM with the thread
Open it automatically with that thread...

# Iteration 6 (16/11/2024):
Changed UI
Added feature to Check and Stop Running Models
Added Modularity to the code
Added Image Support (LLama vision and Llava)

# Iteration 7 (17/11/2024):
Completely modularized the threads codes
Refactored the image logic Completely


# To do:
- Save the images in local file, store in thread json
- try except in the write_stream to save the half response at least in case of error


# Currently working on:
- Comment out saved thread successfully around line 450 app.py
- Update the docstring-s of functions in the app_threads file
- Move the LLM model sidebar out of app.py

- Update the parse image function to run subprocess and copy image from abs path to local folder
- Check the thread_image_folder existence from the parse image function as it can be checked from anywhere else (if set in the st.ssss, it will fail in case new thread is created afterwards)
- Downscaled image if greater than 720*720

# Future plans:
Integrate lang-chain in it


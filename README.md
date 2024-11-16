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

# To do:
- Change the temp_image clear from app.py to load_thread
- So that, only the images of the thread are saved and rest all cleared

- Instead of saving the thread data like model and all in separate files, save it in threads json directly 

- Save the images in local file, store both local_path and user_path in the thread json

- try except in the write_stream to save the half response at least in case of error

- Save temp folder and thread folder names in the global variables / st.ssss

- Check threads delete folder is auto created or not

# Future plans:
Integrate lang-chain in it


1. Make sure that Ollama is installed in your environment.
2. If not, install it like:
    ```bash
    pip install ollama
    ```
3. Download the models using:
    ```bash
    ollama run llama3.1:latest
    ```
4. Run the Ollama server using:
    ```bash
    ollama start
    ```
5. No need to run the model separately, it will be started automatically from my app.
6. Images can be attached like:
    ```text
    +++{image: ["absolute/path/to/image", "another_one"]}+++
    ```
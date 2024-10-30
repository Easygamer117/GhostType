# GhostType

**GhostType** is a Python tool that runs in the background and automatically sends highlighted text to OpenAI when a specific key combination is pressed. It answers questions based on the highlighted text and can insert the response directly as if typed by the user.

> **Note**: GhostType has been tested exclusively on Windows 11.

## Features

- **Automatic Text Detection and Response**: Highlight any text and press `Ctrl + Space` to send it to ChatGPT. The response is saved and used when you switch to write mode.
- **Toggle Write Mode**: Use `Ctrl + Tab` to switch to write mode, where the response is automatically typed in as if you're writing it yourself. Each keystroke you make will type the next character of the ChatGPT response.
- **Process Monitoring**: Automatically exits if certain monitored processes (e.g., Task Manager, Process Explorer) are detected.
- **Mute Indicator**: Mutes the system to indicate that a request has been sent to OpenAI and shows the response status.

## Installation

1. **Requirements**: Ensure Python is installed and you have an OpenAI API key.
2. **Dependencies**: Install the required packages with the following command:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variable**: Set your OpenAI API key as an environment variable named `OPENAI_API_KEY` to access the OpenAI API.

## Usage

1. **Start the Program**: Run `main.py`:

   ```bash
   python main.py
   ```

2. **Keyboard Shortcuts**:
   - `Ctrl + Space`: Sends highlighted text to OpenAI and copies the response to the clipboard.
   - `Ctrl + Tab`: Toggles write mode, allowing the response to be automatically typed in.
   - `Esc`: Exits the program.

## Configuration

You can customize the configurations in the code:

- **Keybindings**: Modify the `KEYBINDS` dictionary to set custom keyboard shortcuts.
- **Process Monitoring**: Enable or disable process monitoring with the `PROCESS_MONITORING` variable.
- **Process List**: The `BLACKLISTED_PROCESSES` list contains the processes that trigger an automatic program exit when launched.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
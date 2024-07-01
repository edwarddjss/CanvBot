# Canvas Discord Bot

A Discord bot that integrates with the Canvas Learning Management System to fetch and process assignment information for users. The bot can create text channels for upcoming assignments and send reminders about due dates.

## Features

- Fetch assignments from Canvas.
- Create text channels for assignments in Discord.
- Send reminders about upcoming due dates.
- Connect API keys for Canvas.
- Dropdown selection for current courses.

## Prerequisites

- Python 3.8+
- Discord Bot Token
- Canvas API Key
- SQLite3

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add your Discord bot token:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    ```

4. Initialize the database:
    ```sh
    python -c "from canvasDB import init_db; init_db()"
    ```

## Usage

1. Run the bot:
    ```sh
    python canvasDiscord.py
    ```

2. Invite the bot to your server and use the `/connect` command to connect your Canvas API key.

## Commands

### `/test`
- Description: A simple test command to check if the bot is working.
- Usage: `/test`

### `/connect`
- Description: Connects your Canvas API Key.
- Usage: `/connect YOUR_API_KEY`

### `/selectcourses`
- Description: Opens a dropdown to select current courses.
- Usage: `/selectcourses`

## Code Overview

### canvasDiscord.py

This is the main bot script that handles the Discord bot's functionality, including fetching assignments from Canvas, creating text channels, and sending reminders.

Key functions and classes:
- `extract_assignment_info(assignments)`: Extracts assignment information from the Canvas API response.
- `fetch_and_process_assignments(api_key, course_id, guild_id)`: Fetches assignments and processes them.
- `create_text_channel(name, due_date, guild_id)`: Creates a text channel for an assignment.
- `get_courses(user_id)`: Retrieves active courses for the user.
- `CourseSelect(discord.ui.Select)`: Dropdown select menu for courses.
- `CourseView(discord.ui.View)`: View for displaying the dropdown select menu.
- `on_ready()`: Event handler for when the bot is ready.
- `schedule_fetch_assignments()`: Schedules periodic fetching of assignments.

### canvasDB.py

This script handles database interactions using SQLite. It includes functions to initialize the database, insert and retrieve API keys and course information.

Key functions:
- `init_db()`: Initializes the database and creates tables.
- `get_api_key(user_id)`: Retrieves the API key for a user.
- `insert_api_key(user_id, api_key)`: Inserts or updates an API key for a user.
- `insert_user_course(user_id, course_id, course_name)`: Inserts or updates a user's course information.
- `get_course_id_by_name(user_id, course_name)`: Retrieves a course ID by its name.
- `get_course_ids(user_id)`: Retrieves all course IDs for a user.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [discord.py](https://github.com/Rapptz/discord.py) - Python library for Discord.
- [aiohttp](https://github.com/aio-libs/aiohttp) - Asynchronous HTTP client/server framework.
- [requests](https://github.com/psf/requests) - Simple HTTP library for Python.
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Python library to load environment variables from a `.env` file.
- [dateutil](https://github.com/dateutil/dateutil) - Extensions to the standard Python datetime module.

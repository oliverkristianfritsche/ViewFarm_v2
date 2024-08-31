# Project Name

## Table of Contents
- [Prerequisites](#prerequisites)
- [Cloning the Repository](#cloning-the-repository)
- [Configuring the `config.json` File](#configuring-the-configjson-file)
- [Running the `build.ps1` Script](#running-the-buildps1-script)
- [Running the `run.ps1` Script](#running-the-runps1-script)

## Prerequisites
- **PowerShell 5.1 or later**
- **Python 3.8 or later**
- **Docker installed

## Cloning the Repository
1. Open PowerShell or your preferred terminal.
2. Clone the repository by running the following command:
    ```bash
    git clone https://github.com/oliverkristianfritsche/ViewFarm_v2
    ```
3. Navigate to the project directory:
    ```bash
    cd ViewFarm_v2
    ```

## Configuring the `config.json` File
1. Create a new file named `config.json` in the root directory of the project.
2. Add the following structure to the file:
    ```json
    {
      "botid": "your_bot_id",
      "YOUTUBE_API_KEY": "your_youtube_api_key",
      "youtubescrapper": {
        "searchBy": "hashtag",
        "searchValue": "your_search_value",
        "maxResults": 50,
        "order": "viewCount",
        "shorts_category_id": "0",
        "max_short_length": 60
      },
      "CLIENT_ID": "your_client_id",
      "CLIENT_SECRET": "your_client_secret",
      "USER_AGENT": "your_user_agent",
      "subreddits": "your_subreddits",
      "num_posts": 11,
      "target_language": ["en", "es", "hi", "pt", "ar"],
      "speaker_file": "/root/speakers/speaker_americanpyscho.wav",
      "audio_speed": 2.5,
      "video_speed": 1.3,
      "max_video_length": 60
    }
    ```
3. Replace the placeholder values with your own:
    - `your_bot_id`: A unique identifier for your bot
    - `your_youtube_api_key`: Your YouTube API key
    - `your_search_value`: The value to search for on YouTube
    - `your_client_id`: Your Reddit client ID
    - `your_client_secret`: Your Reddit client secret
    - `your_user_agent`: Your Reddit user agent
    - `your_subreddits`: The subreddits to scrape

## Running the `build.ps1` Script
1. Open PowerShell and navigate to the root directory of the project.
2. Run the `build.ps1` script by typing:
    ```bash
    .\build.ps1
    ```
3. The script will install the required dependencies and build the project.

## Running the `run.ps1` Script
1. Ensure that you have correctly configured the `config.json` file with your own values.
2. Open PowerShell and navigate to the root directory of the project.
3. Run the `run.ps1` script by typing:
    ```bash
    .\run.ps1
    ```
4. The script will start the multilanguage Reddit pipeline.

> **Note:** Make sure to replace the placeholder values in the `config.json` file with your own values before running the `run.ps1` script.

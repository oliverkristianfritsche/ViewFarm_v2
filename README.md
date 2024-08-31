# View Farm

## Table of Contents
- [Prerequisites](#prerequisites)
- [Cloning the Repository](#cloning-the-repository)
- [Configuring the `config.json` File](#configuring-the-configjson-file)
- [Running the `build.ps1` Script](#running-the-buildps1-script)
- [Running the `run.ps1` Script](#running-the-runps1-script)
- [Pipeline Overview](#pipeline-overview)
- [Example Video](#example-video)

## Prerequisites
- **PowerShell 5.1 or later**
- **Python 3.8 or later**
- **Docker installed**

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
    - `botid`: A unique identifier for your bot.
    - `YOUTUBE_API_KEY`: Your YouTube API key used to access YouTube data.
    - `youtubescrapper`:
        - `searchBy`: Criteria for searching on YouTube. Options are `hashtag`, `trending`, or `account`.
        - `searchValue`: The specific value to search for based on the `searchBy` parameter (e.g., the actual hashtag or account name).
        - `maxResults`: The maximum number of search results to return.
        - `order`: The order in which to sort results (e.g., `viewCount`).
        - `shorts_category_id`: ID for the YouTube shorts category.
        - `max_short_length`: The maximum length (in seconds) for short-form videos.
    - `CLIENT_ID`: Your Reddit client ID used to access the Reddit API.
    - `CLIENT_SECRET`: Your Reddit client secret used for API authentication.
    - `USER_AGENT`: The user agent string for Reddit API requests.
    - `subreddits`: A comma-separated list of subreddits from which to scrape stories.
    - `num_posts`: The number of posts to retrieve from each subreddit.
    - `target_language`: A list of target languages for translation (e.g., `["en", "es", "hi", "pt", "ar"]`).
    - `speaker_file`: The path to the audio file used for TTS (text-to-speech) synthesis.
    - `audio_speed`: The speed multiplier for the generated audio.
    - `video_speed`: The speed multiplier for the video playback.
    - `max_video_length`: The maximum length (in seconds) for the final video.

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

> **Note:** This script automatically mounts your Google Drive. If the specified paths do not exist, you must change them in the `./run.ps1` script. Videos will be outputted to `./reprocessio/[language type]`.

## Pipeline Overview
This project showcases a sophisticated and automated content creation pipeline, designed to capitalize on the virality of short-form content, particularly on platforms like YouTube and Reddit.

1. **YouTube Scraping:** The process begins by using the YouTube API to scrape video analysts and links based on criteria like hashtags, trending locations, or specific accounts.
2. **Video Download:** Once the desired videos are identified, they are downloaded using `youtube-dl`.
3. **Reddit Story Collection:** The Reddit API is then utilized to gather popular stories from selected subreddits, ensuring the content is engaging and relevant.
4. **Translation:** Using `deep_translate`, the stories are translated into the target languages specified in the `config.json` file.
5. **Video Overlay:** The downloaded videos and translated Reddit stories are then combined using `MoviePy` to create compelling videos that are primed for short-form content platforms.
6. **Text-to-Speech:** The translated text is converted to speech using the [GTTS package](https://github.com/coqui-ai/TTS).
7. **Content Popularity:** This method is particularly effective for generating viral content, with some pages achieving millions of views across all videos.
8. **Google Drive Integration:** Once the videos are created, they are automatically saved to a Google Drive account in language-specific folders for easy organization and access.
9. **Autoposting:** The final step involves using the Repurpose.io website to automate the posting of these videos to various social media accounts, ensuring consistent and timely content distribution.

## Example Video
You can view an example video created by this pipeline here: `[Add Path to Example Video]`

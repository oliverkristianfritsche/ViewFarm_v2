import requests
import json

# Load cookies from a JSON file
def load_cookies(cookies_file):
    with open(cookies_file, 'r') as f:
        cookies = json.load(f)
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
    return cookies_dict

# Initialize session
session = requests.Session()

# Load cookies and add them to the session
cookies = load_cookies('/root/cookies.json')
session.cookies.update(cookies)

# Example GET request to YouTube Studio
url = 'https://studio.youtube.com/channel/UCzvFvbDrgJ0Cp1Ia-YysqVg/videos/upload?d=ud&filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Send GET request with session
response = session.get(url, headers=headers)

# Check response
if response.status_code == 200:
    print("Successfully accessed the page!")
    print(response.text)
else:
    print(f"Failed to access the page. Status code: {response.status_code}")

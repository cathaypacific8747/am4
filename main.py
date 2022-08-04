import os
from dotenv import load_dotenv

if __name__ == '__main__':
    load_dotenv()

    discord_token = os.getenv('DISCORD_TOKEN')
    am4tools_token = os.getenv('AM4TOOLS_TOKEN')
    if discord_token is None or am4tools_token is None:
        raise AssertionError('Discord and AM4Tools token required!')
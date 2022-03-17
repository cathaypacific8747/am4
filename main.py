import os
from dotenv import load_dotenv()

if __name__ == '__main__':
    load_dotenv()
    discord_token = os.getenv('DISCORD_TOKEN_PRODUCTION' if os.getenv('MODE') == 'PRODUCTION' else 'DISCORD_TOKEN_DEVELOPMENT')
    assert discord_token is not None
    
    print(discord_token)
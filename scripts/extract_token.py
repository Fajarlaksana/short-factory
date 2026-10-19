"""Quick script to extract refresh token from the code we already got"""
import requests
import json

# The code you got
auth_code = "4/1Ab32j93H8YinIVU9EYZqZN9UHaTYE8wJmagGbSycbktwR5aldf12QnthCHs"

# Your credentials
with open('client_secrets.json', 'r') as f:
    secrets = json.load(f)
    client_data = secrets.get('installed', {})
    client_id = client_data.get('client_id', '')
    client_secret = client_data.get('client_secret', '')

# Exchange code for tokens
token_url = "https://oauth2.googleapis.com/token"
data = {
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
    'grant_type': 'authorization_code'
}

response = requests.post(token_url, data=data)
token_data = response.json()

if 'error' in token_data:
    print("Error:", token_data)
else:
    refresh_token = token_data.get('refresh_token')
    access_token = token_data.get('access_token')
    
    print("=" * 70)
    print("✅ YOUR YOUTUBE TOKENS:")
    print("=" * 70)
    print()
    print(f"YOUTUBE_CLIENT_ID={client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
    print()
    print("Now we need your Channel ID.")
    print("Go to: https://www.youtube.com/account_advanced")
    print("Or tell me your channel name/URL and I can help find it")
    print()
    
    # Save
    with open('youtube_tokens.txt', 'w') as f:
        f.write(f"YOUTUBE_CLIENT_ID={client_id}\n")
        f.write(f"YOUTUBE_CLIENT_SECRET={client_secret}\n")
        f.write(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")


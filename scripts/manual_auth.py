"""
Manual YouTube token - uses out-of-band redirect (copy-paste code)
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

print("=" * 70)
print("YouTube Token Generator (Manual Method)")
print("=" * 70)
print()

# Read client secrets
with open('client_secrets.json', 'r') as f:
    secrets = json.load(f)
    client_data = secrets.get('installed', {})
    client_id = client_data.get('client_id', '')
    client_secret = client_data.get('client_secret', '')

# Build authorization URL manually with all required parameters
auth_url = (
    "https://accounts.google.com/o/oauth2/auth?"
    f"client_id={client_id}&"
    "redirect_uri=urn:ietf:wg:oauth:2.0:oob&"
    "response_type=code&"
    "scope=https://www.googleapis.com/auth/youtube.upload&"
    "access_type=offline&"
    "prompt=consent"
)

print("STEP 1: Copy and paste this URL into your browser:")
print()
print(auth_url)
print()
print("=" * 70)
print("STEP 2: Authorize and copy the code")
print("=" * 70)
print()
print("After clicking 'Allow', you'll see a page with a code.")
print("It will say something like:")
print("  'Please copy this code, switch to your application and paste it there:'")
print()
print("Copy that code (the long string) and paste it below:")
print()

auth_code = input("Paste the authorization code here: ").strip()

print()
print("Exchanging code for tokens...")

try:
    # Exchange code for tokens using requests directly
    import requests
    
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
        raise Exception(f"Token exchange failed: {token_data.get('error_description', token_data.get('error'))}")
    
    refresh_token = token_data.get('refresh_token')
    access_token = token_data.get('access_token')
    
    if not refresh_token:
        raise Exception("No refresh token received. Make sure you included 'prompt=consent' and 'access_type=offline' in the auth URL.")
    
    # Create credentials object
    from google.oauth2.credentials import Credentials
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    
    print("✅ Got credentials!")
    
    # Get channel ID - try with current scopes, if fails we'll get it manually
    channel_id = None
    channel_name = "Your Channel"
    
    try:
        service = build('youtube', 'v3', credentials=creds)
        request = service.channels().list(part='id,snippet', mine=True)
        response = request.execute()
        
        if response.get('items'):
            channel = response['items'][0]
            channel_id = channel['id']
            channel_name = channel['snippet']['title']
            print(f"✅ Got channel info: {channel_name}")
        else:
            print("⚠️  Could not get channel via API, we'll get it manually")
    except Exception as e:
        print(f"⚠️  Could not get channel via API: {e}")
        print("   That's OK - we'll get channel ID manually")
    
    refresh_token = creds.refresh_token
    
    # If we don't have channel ID, ask user
    if not channel_id:
        print()
        print("=" * 70)
        print("We need your YouTube Channel ID")
        print("=" * 70)
        print()
        print("Option 1: Go to https://www.youtube.com/account_advanced")
        print("          Your Channel ID is shown there")
        print()
        print("Option 2: Or visit any video on your channel,")
        print("          click on your channel name,")
        print("          the Channel ID is in the URL")
        print()
        channel_id = input("Paste your Channel ID here (or press Enter to skip for now): ").strip()
        if not channel_id:
            channel_id = "SKIP_FOR_NOW"
            print("⚠️  You can add Channel ID later in your .env file")
    
    print()
    print("=" * 70)
    print("✅ SUCCESS! Here are your tokens:")
    print("=" * 70)
    print()
    print(f"YOUTUBE_CLIENT_ID={client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
    print(f"YOUTUBE_CHANNEL_ID={channel_id}")
    print()
    if channel_id != "SKIP_FOR_NOW":
        print(f"Channel: {channel_name} (ID: {channel_id})")
    print()
    
    # Save to files
    with open('youtube_tokens.txt', 'w') as f:
        f.write(f"YOUTUBE_CLIENT_ID={client_id}\n")
        f.write(f"YOUTUBE_CLIENT_SECRET={client_secret}\n")
        f.write(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")
        f.write(f"YOUTUBE_CHANNEL_ID={channel_id}\n")
    
    # Update YOUR_KEYS.txt
    print("✅ Saved tokens to youtube_tokens.txt")
    print()
    print("Copy these 4 values to your hosting platform!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()


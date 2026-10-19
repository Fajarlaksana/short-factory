"""
Simple token getter - no redirect URI issues
"""
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

print("=" * 70)
print("Simple YouTube Token Generator")
print("=" * 70)
print()

# Step 1: Show authorization URL
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secrets.json', SCOPES)

auth_url, _ = flow.authorization_url(
    access_type='offline',
    prompt='consent',
    redirect_uri='http://localhost:8080'
)

print("STEP 1: Copy and paste this URL into your browser:")
print()
print(auth_url)
print()
print("=" * 70)
print("STEP 2: After clicking Allow, you'll see an error page.")
print("That's OK! Look at the URL in your browser address bar.")
print()
print("It will look like:")
print("http://localhost:8080/?code=4/0AeaYSHC...&scope=...")
print()
print("Or it might say 'connection refused' - that's fine too!")
print("What matters is the URL contains 'code='")
print("=" * 70)
print()

# Get the code from URL
auth_code = input("Paste the ENTIRE URL (or just the code part after 'code='): ").strip()

# Extract just the code if full URL provided
if "code=" in auth_code:
    auth_code = auth_code.split("code=")[1].split("&")[0]

print()
print("Got code, exchanging for tokens...")

# Create a manual authorization response
# The code might already have the redirect_uri, or we add it
if auth_code.startswith("http://"):
    # User pasted full URL
    authorization_response = auth_code
else:
    # User pasted just code, build full response
    redirect_uri = "http://localhost:8080"
    authorization_response = f"{redirect_uri}/?code={auth_code}"

try:
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    
    print("✅ Got credentials!")
    
    # Get channel ID
    service = build('youtube', 'v3', credentials=creds)
    request = service.channels().list(part='id,snippet', mine=True)
    response = request.execute()
    
    if not response.get('items'):
        print("❌ Could not get channel info")
        exit(1)
    
    channel = response['items'][0]
    channel_id = channel['id']
    channel_name = channel['snippet']['title']
    
    # Read client info
    with open('client_secrets.json', 'r') as f:
        secrets = json.load(f)
        client_data = secrets.get('installed', {})
        client_id = client_data.get('client_id', '')
        client_secret = client_data.get('client_secret', '')
    
    refresh_token = creds.refresh_token
    
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
    print(f"Channel: {channel_name}")
    print()
    
    # Save to file
    with open('youtube_tokens.txt', 'w') as f:
        f.write(f"YOUTUBE_CLIENT_ID={client_id}\n")
        f.write(f"YOUTUBE_CLIENT_SECRET={client_secret}\n")
        f.write(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")
        f.write(f"YOUTUBE_CHANNEL_ID={channel_id}\n")
    
    print("✅ Saved to youtube_tokens.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry again with the authorization code")


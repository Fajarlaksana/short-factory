"""
Get fresh YouTube token - with timeout protection
"""
import requests
import json
from datetime import datetime

print("=" * 70)
print("YouTube Token Generator (Fresh Code)")
print("=" * 70)
print()

# Read credentials
with open('client_secrets.json', 'r') as f:
    secrets = json.load(f)
    client_data = secrets.get('installed', {})
    client_id = client_data.get('client_id', '')
    client_secret = client_data.get('client_secret', '')

# Build authorization URL
auth_url = (
    "https://accounts.google.com/o/oauth2/auth?"
    f"client_id={client_id}&"
    "redirect_uri=urn:ietf:wg:oauth:2.0:oob&"
    "response_type=code&"
    "scope=https://www.googleapis.com/auth/youtube.upload&"
    "access_type=offline&"
    "prompt=consent"
)

print("STEP 1: Copy this URL and open it NOW in your browser:")
print()
print(auth_url)
print()
print("=" * 70)
print("STEP 2: Get the code IMMEDIATELY (it expires in ~1 minute!)")
print("=" * 70)
print()
print("After clicking Allow, you'll see a code.")
print("Copy it RIGHT NOW and paste here:")
print()

auth_code = input("Authorization code: ").strip()

print()
print("Exchanging code for tokens (with 10 second timeout)...")

try:
    # Exchange with timeout
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        'code': auth_code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }
    
    # Use timeout to prevent hanging
    response = requests.post(token_url, data=data, timeout=10)
    token_data = response.json()
    
    if 'error' in token_data:
        print(f"❌ Error: {token_data}")
        if 'invalid_grant' in token_data.get('error', ''):
            print("\n⚠️  Code expired or already used. Get a fresh code and try again.")
        exit(1)
    
    refresh_token = token_data.get('refresh_token')
    if not refresh_token:
        print("❌ No refresh token received!")
        print("Response:", token_data)
        exit(1)
    
    print("✅ SUCCESS! Got refresh token!")
    print()
    print("=" * 70)
    print("YOUR YOUTUBE TOKENS:")
    print("=" * 70)
    print()
    print(f"YOUTUBE_CLIENT_ID={client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
    print()
    print("✅ Save these to your .env file!")
    print()
    
    # Save to files
    with open('youtube_tokens.txt', 'w') as f:
        f.write(f"YOUTUBE_CLIENT_ID={client_id}\n")
        f.write(f"YOUTUBE_CLIENT_SECRET={client_secret}\n")
        f.write(f"YOUTUBE_REFRESH_TOKEN={refresh_token}\n")
    
    print("✅ Saved to youtube_tokens.txt")
    print()
    print("Next: We'll get your Channel ID separately")
    
except requests.Timeout:
    print("❌ Request timed out. Try again.")
except Exception as e:
    print(f"❌ Error: {e}")


import requests
import re
import os
import time

# --- CONFIGURATION ---
INPUT_FILE = "links.txt"
SAVE_FOLDER = "Repository_Images"

# We are searching for this specific pattern in the entire HTML code
# This will find it regardless of whether it's in 'src', 'data-src', or a script
URL_PATTERN = r'https://images\.merolagani\.com//Uploads/Repository/[^"\'>\s]+\.(jpg|gif)'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

print("🔍 Deep Search Mode Enabled.")
print(f"📂 Reading from: {INPUT_FILE}\n")

if not os.path.exists(INPUT_FILE):
    print("❌ Error: links.txt not found.")
    input("Press Enter to exit...")
    exit()

with open(INPUT_FILE, 'r') as f:
    links = f.readlines()

count = 0

for i, link in enumerate(links):
    link = link.strip()
    if not link: continue

    print(f"[{i+1}] Scanning: {link}")

    try:
        response = requests.get(link, headers=HEADERS, timeout=15)
        
        # Use Regex to find the pattern in the RAW HTML
        # This bypasses the need for HTML tags/attributes
        matches = re.findall(URL_PATTERN, response.text, re.IGNORECASE)

        if matches:
            # matches usually returns a list of tuples because of the (groups) in regex
            # We need to reconstruct the full match or just find the first occurrence
            full_matches = re.finditer(URL_PATTERN, response.text, re.IGNORECASE)
            
            for match in full_matches:
                img_url = match.group(0) # Get the full matched URL
                
                # Clean URL if needed (handle html entities if any)
                img_url = img_url.replace("&amp;", "&")
                
                filename = img_url.split("/")[-1].split("?")[0]
                save_path = os.path.join(SAVE_FOLDER, filename)

                # Avoid re-downloading
                if os.path.exists(save_path):
                    print(f"   ⏩ Already exists: {filename}")
                    continue

                print(f"   🎯 Found: {img_url}")
                
                # Download
                try:
                    img_res = requests.get(img_url, headers=HEADERS, stream=True)
                    if img_res.status_code == 200:
                        with open(save_path, 'wb') as f:
                            f.write(img_res.content)
                        print(f"   ✅ Downloaded: {filename}")
                        count += 1
                    else:
                        print(f"   ❌ Download failed (Error {img_res.status_code})")
                except Exception as e:
                    print(f"   ❌ Download error: {e}")
        else:
            print("   ⚠️ Pattern not found in source code.")
            
        time.sleep(0.5)

    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n🎉 Finished! Downloaded {count} new images.")
input("Press Enter to close...")
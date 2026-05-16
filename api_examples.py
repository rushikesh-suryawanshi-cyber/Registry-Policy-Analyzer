import urllib.request
import json
import urllib.parse

def fetch(url):
    print(f"\n--- Fetching {url} ---")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"Status: {response.status}")
            print(f"Total Count: {data.get('total_count')}")
            for i, item in enumerate(data.get('items', [])[:2]):
                print(f"  {i+1}. {item.get('name')} - {item.get('display_name')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    base_url = "http://127.0.0.1:8000"
    
    # 1. Keyword search for "CD-ROM"
    q_param = urllib.parse.quote('"CD-ROM"')
    fetch(f"{base_url}/search/keyword?q={q_param}")
    
    # 2. Registry search
    key_param = urllib.parse.quote('Software\\Policies\\Microsoft')
    fetch(f"{base_url}/search/registry?key={key_param}")
    
    # 3. Category search
    cat_param = urllib.parse.quote('Windows Components')
    fetch(f"{base_url}/search/category?path={cat_param}")
    
    # 4. Vendor search
    vendor_param = urllib.parse.quote('Windows')
    fetch(f"{base_url}/search/vendor?name={vendor_param}")

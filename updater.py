import json
import urllib.request

with open('config.json', 'r') as f:
    config = json.load(f)

altstore_source = {
    "name": config["name"],
    "subtitle": config["subtitle"],
    "description": config["description"],
    "iconURL": config["iconURL"],
    "website": config["website"],
    "tintColor": config["tintColor"],
    "apps": []
}

req_headers = {'User-Agent': 'Mozilla/5.0'}

for repo in config["monitor_repos"]:
    try:
        api_url = f"https://github.com{repo}/releases/latest"
        req = urllib.request.Request(api_url, headers=req_headers)
        with urllib.request.urlopen(req) as response:
            release_data = json.loads(response.read().decode())
            
        ipa_asset = None
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".ipa"):
                ipa_asset = asset
                break
                
        if not ipa_asset:
            continue
            
        repo_info_url = f"https://github.com{repo}"
        req_repo = urllib.request.Request(repo_info_url, headers=req_headers)
        with urllib.request.urlopen(req_repo) as rep_res:
            repo_data = json.loads(rep_res.read().decode())

        app_entry = {
            "name": repo_data["name"],
            "bundleIdentifier": f"com.custom.{repo_data['name'].lower()}",
            "developerName": repo_data["owner"]["login"],
            "subtitle": repo_data["description"][:50] if repo_data["description"] else "App personalizzata",
            "localizedDescription": release_data.get("body", "Nessuna descrizione."),
            "iconURL": repo_data["owner"]["avatar_url"],
            "versions": [
                {
                    "version": release_data["tag_name"].lstrip('v'),
                    "date": release_data["published_at"].split("T")[0],
                    "localizedDescription": f"Versione {release_data['tag_name']}",
                    "downloadURL": ipa_asset["browser_download_url"],
                    "size": ipa_asset["size"]
                }
            ]
        }
        altstore_source["apps"].append(app_entry)
        
    except Exception as e:
        print(f"Errore con {repo}: {e}")

with open('apps.json', 'w') as f:
    json.dump(altstore_source, f, indent=2)

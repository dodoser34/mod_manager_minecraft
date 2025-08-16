import os
import json
import requests
from tqdm import tqdm
from colorama import Fore, init



init(autoreset=True)



CONFIG_PATH = "config.json"
MODS_LIST_URL = "https://www.dropbox.com/scl/fi/cb3ljpr6p3xmjz2ozdqbc/test.json?rlkey=ypw5mq1pc22j7j655wrmmwv75&e=1&st=x1tkxz1r&dl=1"



def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}



def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)



def choose_mods_folder():
    config = load_config()
    if config.get("mods_path"):
        print("[1] Enter new path")
        print("[2] Use saved path:", config["mods_path"])
        if input("Choose: ") == "2":
            return config["mods_path"]
    path = input("Enter path to your mods folder: ").strip('"')
    config["mods_path"] = path
    save_config(config)
    return path



def download_json():
    try:
        response = requests.get(MODS_LIST_URL)
        response.raise_for_status()
        return response.json()
    except:
        print(Fore.RED + "[!] Failed to download mods list.")
        return None



def download_file(url, dest):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(
            desc=f"⬇ {os.path.basename(dest)}",
            total=total,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))



def get_mods_in_folder(mods_path):
    return {f for f in os.listdir(mods_path) if f.endswith(".jar")}



def process_mods(mods, mods_path):
    current_mods = get_mods_in_folder(mods_path)
    for mod in mods:
        remove = mod["name"].startswith("!")
        name = mod["name"].lstrip("!")
        filename = mod["url"].split("/")[-1]
        url = mod["url"]
        existing = [f for f in current_mods if f.lower().startswith(name.lower())]

        if remove:
            for f in existing:
                os.remove(os.path.join(mods_path, f))
                print(Fore.YELLOW + f"🗑 Removed: {f}")
            continue

        if filename in current_mods:
            print(Fore.GREEN + f"✅ {filename} already installed.")
        else:
            for f in existing:
                os.remove(os.path.join(mods_path, f))
                print(Fore.YELLOW + f"♻ Old version removed: {f}")
            print(Fore.CYAN + f"⬇ Installing: {filename}")
            download_file(url, os.path.join(mods_path, filename))
    print(Fore.GREEN + "\n✅ Mods updated.")



def main():
    mods_path = choose_mods_folder()
    if not os.path.isdir(mods_path):
        print(Fore.RED + "❌ Folder not found.")
        return
    print(Fore.CYAN + "📡 Downloading mods list...")
    mods = download_json()
    if mods:
        process_mods(mods, mods_path)



if __name__ == "__main__":
    main()
    input("Press Enter to exit...")

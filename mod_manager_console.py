import os
import json
import requests
import shutil
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

CONFIG_PATH = "config.json"
MODS_LIST_URL = "https://www.dropbox.com/scl/fi/02gwucw79u70igfyz49pb/mods.json?rlkey=ttwhg17ccsbh38odthfjfi9tn&st=rz7iah0j&dl=1"

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
        print("[1] Ввести путь заново")
        print("[2] Использовать прежний путь:", config["mods_path"])
        choice = input("Выберите: ")
        if choice == "2":
            return config["mods_path"]

    path = input("Введите путь к папке с модами (где находится 'mods'): ").strip('"')
    config["mods_path"] = path
    save_config(config)
    return path

def download_json():
    response = requests.get(MODS_LIST_URL)
    if response.status_code != 200:
        print(Fore.RED + "[!] Не удалось скачать список модов.")
        return None
    return response.json()

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
                print(Fore.YELLOW + f"🗑 Удалён мод: {f}")
            continue

        # Обновление / установка
        if filename in current_mods:
            print(Fore.GREEN + f"✅ {filename} уже установлен.")
        else:
            for f in existing:
                os.remove(os.path.join(mods_path, f))
                print(Fore.YELLOW + f"♻ Удалена старая версия: {f}")

            print(Fore.CYAN + f"⬇ Установка/обновление: {filename}")
            download_file(url, os.path.join(mods_path, filename))

    print(Fore.GREEN + "\n✅ Все моды обновлены. Приятной игры на BANGUN!")

def main():
    mods_path = choose_mods_folder()

    if not os.path.isdir(mods_path):
        print(Fore.RED + "❌ Указанная папка не существует.")
        return

    print(Fore.CYAN + "📡 Загружаем список модов...")
    mods = download_json()
    if mods:
        process_mods(mods, mods_path)

if __name__ == "__main__":
    main()

import os
import json
import requests
import customtkinter as ctk
from tkinter import filedialog

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")  # Можно оставить или заменить

YELLOW = "#FFD700"
WHITE = "#FFFFFF"
BLACK = "#000000"

SETTINGS_FILE = "settings.json"
MODS_JSON_URL = "https://www.dropbox.com/scl/fi/02gwucw79u70igfyz49pb/mods.json?rlkey=ttwhg17ccsbh38odthfjfi9tn&st=rz7iah0j&dl=1"

LANG = {
    "RU": {
        "title": "Mod Manager",
        "browse": "📁 Обзор",
        "start": "🚀 Начать установку",
        "language": "🌐 Язык: RU",
        "select_folder_error": "❌ Неверный путь!",
        "download_error": "❌ Не удалось скачать список модов.",
        "installing": "📥 Установка: ",
        "installed": "✅ Установлен: ",
        "updating": "🔁 Обновление: ",
        "updated": "✅ Обновлён: ",
        "uptodate": "✔️ Актуален: ",
        "removed": "🗑️ Удалён: ",
        "done": "🎉 Все моды установлены!",
        "download_fail": "❌ Ошибка при загрузке: ",
    },
    "EN": {
        "title": "Mod Manager",
        "browse": "📁 Browse",
        "start": "🚀 Start Installation",
        "language": "🌐 Language: EN",
        "select_folder_error": "❌ Invalid path!",
        "download_error": "❌ Failed to download mod list.",
        "installing": "📥 Installing: ",
        "installed": "✅ Installed: ",
        "updating": "🔁 Updating: ",
        "updated": "✅ Updated: ",
        "uptodate": "✔️ Up to date: ",
        "removed": "🗑️ Removed: ",
        "done": "🎉 All mods installed!",
        "download_fail": "❌ Download error: ",
    }
}

class ModManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.language = "RU"
        self.set_lang()

        self.saved_path = self.load_path()

        self.title(LANG[self.language]["title"])
        self.geometry("512x512")

        self.title_label = ctk.CTkLabel(
            self,
            text=self.lang["title"],
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=WHITE,
        )
        self.title_label.pack(pady=10)

        self.path_entry = ctk.CTkEntry(self, width=380)
        self.path_entry.pack(pady=5)

        if self.saved_path:
            self.path_entry.insert(0, self.saved_path)

        self.browse_btn = ctk.CTkButton(
            self,
            text=self.lang["browse"],
            command=self.browse_path,
            fg_color=YELLOW,
            hover_color="#B8860B",
            text_color=BLACK,
        )
        self.browse_btn.pack(pady=5)

        self.start_btn = ctk.CTkButton(
            self,
            text=self.lang["start"],
            command=self.process_mods,
            fg_color=YELLOW,
            hover_color="#B8860B",
            text_color=BLACK,
        )
        self.start_btn.pack(pady=10)

        self.progress = ctk.CTkProgressBar(self, width=300, progress_color=YELLOW)
        self.progress.set(0)
        self.progress.pack(pady=(10, 5))

        self.progress_label = ctk.CTkLabel(self, text="", text_color=WHITE)
        self.progress_label.pack()

        self.logbox = ctk.CTkTextbox(self, height=200, width=480)
        self.logbox.pack(pady=10)

        self.lang_btn = ctk.CTkButton(
            self,
            text=self.lang["language"],
            command=self.toggle_language,
            fg_color=YELLOW,
            hover_color="#B8860B",
            text_color=BLACK,
        )
        self.lang_btn.pack(pady=5)

    def set_lang(self):
        self.lang = LANG[self.language]

    def browse_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def log(self, message):
        self.logbox.insert("end", message + "\n")
        self.logbox.see("end")

    def toggle_language(self):
        self.language = "EN" if self.language == "RU" else "RU"
        self.set_lang()

        self.title(self.lang["title"])
        self.title_label.configure(text=self.lang["title"])
        self.browse_btn.configure(text=self.lang["browse"])
        self.start_btn.configure(text=self.lang["start"])
        self.lang_btn.configure(text=self.lang["language"])

    def save_path(self, path):
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"last_path": path}, f)

    def load_path(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f).get("last_path", "")
        return ""

    def process_mods(self):
        path = self.path_entry.get().strip()
        if not os.path.exists(path):
            self.log(self.lang["select_folder_error"])
            return

        self.save_path(path)

        try:
            mods_json = requests.get(MODS_JSON_URL).json()
        except Exception:
            self.log(self.lang["download_error"])
            return

        for mod in mods_json:
            name = mod["name"]
            url = mod["url"]
            version = mod["version"]

            filename = os.path.basename(url)
            dest = os.path.join(path, filename)

            installed = self.find_installed_mod(path, name)

            if name.startswith("!"):
                actual_name = name[1:]
                self.remove_mods(path, actual_name)
                self.log(self.lang["removed"] + actual_name)
                continue

            if not installed:
                self.log(self.lang["installing"] + name)
                self.download_with_progress(url, dest)
                self.log(self.lang["installed"] + name)

            elif version not in installed:
                self.log(self.lang["updating"] + name)
                self.remove_mods(path, name)
                self.download_with_progress(url, dest)
                self.log(self.lang["updated"] + name)

            else:
                self.log(self.lang["uptodate"] + name)

        self.progress.set(0)
        self.progress_label.configure(text="")
        self.log(self.lang["done"])

    def find_installed_mod(self, path, modname):
        files = os.listdir(path)
        versions = []
        for f in files:
            if f.lower().startswith(modname.lower()) and f.endswith(".jar"):
                versions.append(f)
        return " ".join(versions) if versions else None

    def remove_mods(self, path, modname):
        for f in os.listdir(path):
            if f.lower().startswith(modname.lower()) and f.endswith(".jar"):
                os.remove(os.path.join(path, f))

    def download_with_progress(self, url, dest_path):
        try:
            response = requests.get(url, stream=True)
            total = int(response.headers.get("content-length", 0))

            with open(dest_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(1024 * 16):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = downloaded / total if total else 0
                        self.progress.set(percent)
                        self.progress_label.configure(text=f"{int(percent * 100)}%")
                        self.update_idletasks()
        except Exception as e:
            self.log(self.lang["download_fail"] + str(e))


if __name__ == "__main__":
    app = ModManagerApp()
    app.mainloop()

import json
import os

class Settings:
    def __init__(self):
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.fullscreen = False
        self.filepath = "settings.json"
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    self.music_volume = data.get("music_volume", 0.5)
                    self.sfx_volume = data.get("sfx_volume", 0.5)
                    self.fullscreen = data.get("fullscreen", False)
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump({
                    "music_volume": self.music_volume,
                    "sfx_volume": self.sfx_volume,
                    "fullscreen": self.fullscreen
                }, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

# Global settings instance
settings = Settings()

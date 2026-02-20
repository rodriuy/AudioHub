"""AudioHub launcher"""

from pathlib import Path
import customtkinter as ctk
from audio_hub.config import SettingsManager
from audio_hub.backend import AudioManager
from audio_hub.ui import AudioHubPro
from audio_hub.logger import get_logger


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def main() -> None:
    logger = get_logger("audio_hub")
    settings = SettingsManager(path=Path.cwd() / "settings.json")
    manager = AudioManager()
    app = AudioHubPro(settings=settings, manager=manager)
    app.mainloop()


if __name__ == "__main__":
    main()

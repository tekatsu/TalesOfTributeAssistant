import os
import cv2
import pytesseract
import numpy as np
from threading import Thread
import asyncio
import json

try:
    import decky_plugin
except ImportError:
    print("Warning: 'decky_plugin' not available. Running in standalone mode.")
    decky_plugin = None

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Make configurable if needed

# Comprehensive card database for all decks
card_database = {
    "Drake of Blades": {"priority": 10, "effect": "Gain Gold and Prestige boost"},
    "Insatiable Thirst": {"priority": 9, "effect": "Damages opponent Prestige"},
    "Midnight Raid": {"priority": 8, "effect": "Draw and gain Gold"},
    "Blackfeather Knave": {"priority": 7, "effect": "Gold generation over time"},
    "Prestigious Errand": {"priority": 9, "effect": "Prestige gain"},
    "Coin Seeker": {"priority": 6, "effect": "Gold acceleration"},
    "Knavish Gamble": {"priority": 7, "effect": "Risk-reward play"}
}

class Plugin:
    def __init__(self):
        self.active = True
        self.last_suggestion = "AI Thinking..."
        self.game_state = {
            "hand": [],
            "tavern": [],
            "played_cards": [],
            "opponent_cards": [],
            "active_decks": [],
            "remaining_deck": [],
            "prestige": 0,
            "gold": 0,
            "power": 0
        }
        self.overlay_thread = Thread(target=self.run_overlay, daemon=True)
        self.overlay_thread.start()

    def capture_screen(self):
        """Capture the current screen for card detection."""
        # Check if grim is available
        if os.system("which grim") == 0:
            os.system("grim /tmp/screen.png")
            return cv2.imread("/tmp/screen.png")
        else:
            print("Grim is not available. Skipping screen capture.")
            return None

    def extract_cards(self):
        """Use OCR to detect cards from the screen."""
        image = self.capture_screen()
        if image is None:
            return []
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang="eng")
        return [line.strip() for line in text.split("\n") if line.strip()]

    def update_game_state(self):
        """Update the game state based on OCR-detected cards."""
        detected_cards = self.extract_cards()
        self.game_state["tavern"] = [card for card in detected_cards if card in card_database]
        self.game_state["hand"] = [card for card in detected_cards if "Hand" in card]
        self.game_state["played_cards"] = [card for card in detected_cards if "Played" in card]
        self.game_state["opponent_cards"] = [card for card in detected_cards if "Opponent" in card]
        self.game_state["remaining_deck"] = [card for card in detected_cards if "Deck" in card]

    def suggest_move(self):
        """AI-driven move suggestion based on game state."""
        self.update_game_state()

        best_card = max(
            self.game_state["tavern"],
            key=lambda card: card_database.get(card, {}).get("priority", 0),
            default=None
        )
        
        if best_card:
            return f"BUY {best_card} ({card_database[best_card]['effect']})"

        if "Rajhin available" in self.game_state["active_decks"] and "Opponent gaining Prestige" in self.game_state["opponent_cards"]:
            return "Use Rajhin to deny opponent Prestige gains!"
        
        if "Duke of Crows available" in self.game_state["active_decks"] and self.game_state["gold"] >= 5:
            return "Use Duke of Crows for extra Gold boost!"

        return "Maintain economy, buy high-impact cards, deny opponent resources."

    def run_overlay(self):
        """Display AI suggestions via Decky Loader's UI."""
        if not decky_plugin:
            print("Decky Loader not available. Skipping overlay.")
            return

        async def update_ui():
            while self.active:
                suggestion = self.suggest_move()
                self.last_suggestion = suggestion
                await decky_plugin.emit_event("update_suggestion", {"suggestion": suggestion})
                await asyncio.sleep(2)

        asyncio.run(update_ui())

    async def _main(self):
        """Main loop for Decky Loader integration."""
        while self.active:
            self.last_suggestion = self.suggest_move()
            await asyncio.sleep(2)

    async def enable(self):
        """Enable the plugin."""
        self.active = True
        return "Assistant Enabled"

    async def disable(self):
        """Disable the plugin."""
        self.active = False
        return "Assistant Disabled"

    async def toggle(self):
        """Toggle plugin activity."""
        self.active = not self.active
        return "Toggled Assistant"

    async def get_status(self):
        """Get the plugin's status."""
        return {"active": self.active, "suggestion": self.last_suggestion}

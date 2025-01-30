import os
import time
import cv2
import pytesseract
import numpy as np
import subprocess
import decky_plugin
import pygetwindow as gw
import json
import tkinter as tk
from threading import Thread

# Set up OCR
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Define screen capture function
def capture_screen():
    os.system("grim /home/deck/TalesOfTributeAssistant/screen.png")  # Use 'grim' for Steam Deck
    return cv2.imread("/home/deck/TalesOfTributeAssistant/screen.png")

# Extract text from screenshot
def extract_cards():
    image = capture_screen()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang="eng")

    detected_cards = []
    for line in text.split("\n"):
        detected_cards.append(line.strip())

    return detected_cards

# Comprehensive card database with effects and synergies
card_database = {
    "Drake of Blades": {"type": "Gold/Prestige", "effect": "Gain Gold and Prestige boost", "priority": 10},
    "Insatiable Thirst": {"type": "Aggro", "effect": "Directly damages opponent’s Prestige", "priority": 9},
    "Midnight Raid": {"type": "Draw/Gold", "effect": "Draw cards and gain extra Gold", "priority": 8},
    "Blackfeather Knave": {"type": "Gold Engine", "effect": "Increase Gold per turn", "priority": 7},
    "Prestigious Errand": {"type": "Prestige", "effect": "Gains Prestige without needing Power", "priority": 9},
    "Coin Seeker": {"type": "Gold", "effect": "Increase Gold gain significantly", "priority": 6},
    "Knavish Gamble": {"type": "Risk/Reward", "effect": "Gain Power but may lose Gold", "priority": 7}
}

# Track game state (played cards, tavern, current hands, opponent decks, and active decks)
game_state = {
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

def update_game_state():
    detected_cards = extract_cards()
    game_state["tavern"] = [card for card in detected_cards if "Tavern" in card]
    game_state["hand"] = [card for card in detected_cards if "Hand" in card]
    game_state["played_cards"].extend([card for card in detected_cards if "Played" in card])
    game_state["opponent_cards"].extend([card for card in detected_cards if "Opponent" in card])
    game_state["remaining_deck"] = [card for card in detected_cards if "Deck" in card]

# AI Strategy Logic
def suggest_move():
    update_game_state()
    
    # Determine best card to buy based on available Tavern cards and game state
    best_card = None
    highest_value = 0
    for card in game_state["tavern"]:
        if card in card_database:
            card_data = card_database[card]
            value = card_data["priority"]
            
            # Adjust priority based on game state
            if game_state["gold"] < 5:
                value -= 2  # Reduce priority if we don't have enough gold
            if game_state["prestige"] >= 30:
                value += 3  # Increase priority if we are close to winning
            if value > highest_value:
                best_card = card
                highest_value = value
    
    if best_card:
        return f"BUY {best_card} ({card_database[best_card]['effect']})"
    
    # Patron Strategy - React based on game state and opponent moves
    if "Rajhin available" in game_state["active_decks"] and "Opponent gaining Prestige" in game_state["opponent_cards"]:
        return "Use Rajhin to deny opponent Prestige gains!"
    
    if "Duke of Crows available" in game_state["active_decks"] and game_state["gold"] >= 5:
        return "Use Duke of Crows for extra Gold boost!"
    
    # Prestige Victory Consideration
    if game_state["prestige"] >= 35 and game_state["gold"] > 5:
        return "Push for Prestige win! Buy high-value cards and use Patrons!"
    
    # Predicting opponent's next move based on played cards and deck composition
    possible_opponent_moves = [card for card in game_state["opponent_cards"] if card in game_state["remaining_deck"]]
    if possible_opponent_moves:
        return f"Counter Opponent: Watch for {possible_opponent_moves[0]} next!"
    
    # Default Strategy
    return "Maintain economy, buy high-impact cards, deny opponent resources, and track Prestige win!"

# Decky Plugin for Steam Deck Overlay
class Plugin:
    def __init__(self):
        self.active = True
        self.last_suggestion = ""
        self.overlay_thread = Thread(target=self.run_overlay, daemon=True)
        self.overlay_thread.start()

    def get_suggestion(self):
        if not self.active:
            return "Plugin Disabled"

        suggestion = suggest_move()
        self.last_suggestion = suggestion
        return suggestion

    def highlight_card(self):
        return "Highlighting suggested card in UI"

    def toggle(self):
        self.active = not self.active
        return self.active
    
    def run_overlay(self):
        root = tk.Tk()
        root.title("Tales of Tribute Assistant")
        root.geometry("400x300")
        label = tk.Label(root, text="Waiting for game state...", font=("Arial", 14))
        label.pack(pady=20)

        def update_label():
            while self.active:
                move = suggest_move()
                label.config(text=f"Suggested Move: {move}")
                time.sleep(2)

        Thread(target=update_label, daemon=True).start()
        root.mainloop()

# Main loop
if __name__ == "__main__":
    assistant = Plugin()
    while True:
        move = suggest_move()
        print(f"Game State: {game_state} | Suggested Move: {move}")
        time.sleep(2)

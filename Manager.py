import os
import json

# Use a safe data folder inside the user's home directory
data_dir = os.path.join(os.path.expanduser("~"), ".robot_game_data")
os.makedirs(data_dir, exist_ok=True)

class DataManager:
    DATA_FILE = os.path.join(data_dir, "game_data.json")

    def __init__(self):
        self.data = {
            "coins": 0,
            "owned_skins": ["None"],
            "owned_trails": ["None"],
            "equipped_skin": "None",
            "equipped_trail": "None"
        }
        self.load_data()

    def spend_coins(self, amount):
        current = self.get_coins()
        if current >= amount:
            self.set_coins(current - amount)
            return True
        return False

    def load_data(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r") as file:
                    self.data = json.load(file)
            except (json.JSONDecodeError, FileNotFoundError):
                self.data = {
                    "coins": 0,
                    "owned_skins": ["None"],
                    "owned_trails": ["None"],
                    "equipped_skin": "None",
                    "equipped_trail": "None"
                }

    def save_data(self):
        with open(self.DATA_FILE, "w") as file:
            json.dump(self.data, file, indent=4)

    # Coins
    def get_coins(self):
        return self.data.get("coins", 0)

    def set_coins(self, amount):
        self.data["coins"] = amount
        self.save_data()

    # Owned Skins
    def get_owned_skins(self):
        return self.data.get("owned_skins", [])

    def unlock_skin(self, skin_id):
        if skin_id not in self.data["owned_skins"]:
            self.data["owned_skins"].append(skin_id)
            self.save_data()

    # Owned Trails
    def get_owned_trails(self):
        return self.data.get("owned_trails", [])

    def unlock_trail(self, trail_id):
        if trail_id not in self.data["owned_trails"]:
            self.data["owned_trails"].append(trail_id)
            self.save_data()

    # Equipped Skin
    def get_equipped_skin(self):
        return self.data.get("equipped_skin")

    def set_equipped_skin(self, skin_id):
        self.data["equipped_skin"] = skin_id
        self.save_data()

    # Equipped Trail
    def get_equipped_trail(self):
        return self.data.get("equipped_trail")

    def set_equipped_trail(self, trail_id):
        self.data["equipped_trail"] = trail_id
        self.save_data()


class BestTimeManager:
    BEST_TIME_FILE = os.path.join(data_dir, "best_time.txt")

    def __init__(self, filename=None):
        self.file_path = filename if filename else self.BEST_TIME_FILE

    def load_longest_time(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                content = f.read().strip()
                if content == '':
                    return 0
                try:
                    return float(content)
                except ValueError:
                    return 0
        else:
            return 0

    def save_longest_time(self, new_time):
        with open(self.file_path, "w") as file:
            file.write(str(new_time))

    def update_longest_time(self, current_time):
        longest_time = self.load_longest_time()
        if current_time > longest_time:
            self.save_longest_time(current_time)
            return current_time
        return longest_time
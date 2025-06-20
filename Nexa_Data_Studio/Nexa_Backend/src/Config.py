# src/Config.py
import os
import json

class Config:
    """
    Configuration class to manage settings for the application.
    Loads configuration from a JSON file and provides access to settings.
    """

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.settings = {}
        self.load_config()

    def load_config(self):
        """Load configuration from a JSON file."""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            self.settings = json.load(f)

    def get(self, key, default=None):
        """Get a configuration setting by key."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a configuration setting by key and save it."""
        self.settings[key] = value
        self.save_config()

    def save_config(self):
        """Save the current settings to the configuration file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def __getitem__(self, key):
        """Get a configuration setting using dictionary-like access."""
        return self.get(key)

    def __setitem__(self, key, value):
        """Set a configuration setting using dictionary-like access."""
        self.set(key, value)

    def __repr__(self):
        """String representation of the configuration settings."""
        return f"Config(settings={self.settings})"

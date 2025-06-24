# bot_config.py
import json
import os

class BotConfig:
    def __init__(self, config_file='bot_config.json'):
        self.config_file = config_file
        self.default_config = {
            'watermark': {
                'enabled': True,
                'text': '@YourChannel',
                'position': 'bottom-right',
                'opacity': 0.7,
                'font_size': 24,
                'color': 'white',
                'pdf_opacity': 0.3,
                'pdf_angle': 45,
                'pdf_font_size': 48
            },
            'max_file_size': 50 * 1024 * 1024  # 50MB
        }
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load config from file or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.default_config

    def save_config(self):
        """Save current config to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def toggle_watermark(self, enabled: bool = None) -> bool:
        """Toggle watermark status and return new state"""
        if enabled is None:
            self.config['watermark']['enabled'] = not self.config['watermark']['enabled']
        else:
            self.config['watermark']['enabled'] = enabled
        self.save_config()
        return self.config['watermark']['enabled']

    def set_watermark_text(self, new_text: str):
        """Update watermark text"""
        self.config['watermark']['text'] = new_text
        self.save_config()

    def get_watermark_status(self) -> dict:
        """Return current watermark settings"""
        return self.config['watermark']

    def update_watermark_setting(self, key: str, value):
        """Update specific watermark setting"""
        if key in self.config['watermark']:
            self.config['watermark'][key] = value
            self.save_config()

import json
from dataclasses import dataclass, field
from pathlib import Path
from decimal import Decimal

@dataclass
class Settings:
    # Debug and Logging Settings
    DEBUG_LEVEL: int = 1         # 0 = OFF, 1 = INFO, 2 = DEBUG
    LOG_LEVEL: str = "DEBUG"     # e.g. "DEBUG", "INFO", etc.

    # Cielo API Settings (for data collection)
    CIELO_API_KEY: str = "840657fa-1c23-4daf-8c25-65a0e2e26a59"
    CIELO_WS_URL: str = "wss://feed-api.cielo.finance/api/v1/ws"
    CIELO_FILTERS: dict = field(default_factory=lambda: {
        "chains": ["solana"],
        "tx_types": ["swap"],
        "min_usd_value": 500
    })
    CIELO_RECONNECT_DELAY: int = 15  # Seconds to wait before reconnecting

    # Telegram Settings (for communication agents)
    API_ID: str = "26398708"
    API_HASH: str = "f55f7a2e1d251ba7fc30c2a3d37ef4df"
    TARGET_CHANNEL: str = "@mangulica"         # Main alert channel
    TRADEWIZ_CHANNEL: str = "@TradeonNova2Bot"   # Secondary channel
    CA_CHANNEL2: str = "@helenus_trojanbot"      # Additional channel 1
    CA_CHANNEL3: str = "@TradeWiz_Solbot"         # Additional channel 2

    # Directories for Data and Logging
    DATA_DIR: Path = field(default_factory=lambda: Path("data"))
    LOG_DIR: Path = field(default_factory=lambda: Path("logs"))
    LOG_FILE: Path = field(default_factory=lambda: Path("logs") / "main.log")

    def to_serializable_dict(self) -> dict:
        """Convert settings to a serializable dictionary (e.g., for saving to JSON)."""
        serializable = self.__dict__.copy()
        # Convert Path objects to strings
        for key in ['DATA_DIR', 'LOG_DIR', 'LOG_FILE']:
            if key in serializable and isinstance(serializable[key], Path):
                serializable[key] = str(serializable[key])
        return serializable

    def save_to_file(self, filename: str = "settings.json"):
        """Save current settings to a JSON file."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        path = self.DATA_DIR / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_serializable_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str = "settings.json") -> 'Settings':
        """Load settings from a JSON file."""
        try:
            path = Path("data") / filename
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Convert directory strings back to Path objects
            data['DATA_DIR'] = Path(data.get('DATA_DIR', 'data'))
            data['LOG_DIR'] = Path(data.get('LOG_DIR', 'logs'))
            data['LOG_FILE'] = Path(data.get('LOG_FILE', 'logs/main.log'))
            return cls(**data)
        except FileNotFoundError:
            return cls()

# Create a global settings instance
settings = Settings()

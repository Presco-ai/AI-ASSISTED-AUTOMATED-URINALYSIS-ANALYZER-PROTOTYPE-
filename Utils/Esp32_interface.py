from models.enums import ConnectionType
from models.patient import ESP32Config

class ESP32Interface:
    def __init__(self):
        self.config = ESP32Config()
        self.connected = False

    def connect_bluetooth(self, address):
        self.config.bluetooth_address = address
        self.config.connection_type = ConnectionType.BLUETOOTH
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False

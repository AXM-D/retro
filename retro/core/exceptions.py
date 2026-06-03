class RetroError(Exception):
    pass

class SensorError(RetroError):
    pass

class CountermeasureError(RetroError):
    pass

class ProtectionError(RetroError):
    pass

class OSINTError(RetroError):
    pass

class AlertError(RetroError):
    pass

class StorageError(RetroError):
    pass

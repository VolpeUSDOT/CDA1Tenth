from PySide6.QtCore import QObject, QUrl, Signal, QCoreApplication
from PySide6.QtWebSockets import QWebSocket
import signal

class WebSocketClient(QObject):
    '''
    Singleton class to connect to a WebSocket server
    '''
    _instance = None

    message_received = Signal(str)
    connected = Signal()
    disconnected = Signal()

    def __new__(cls, url: str = "ws://localhost:9002"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, url: str = "ws://localhost:9002"):
        if not hasattr(self, 'initialized'):  # Prevent re-initialization
            super().__init__()
            self.url = QUrl(url)
            self.websocket = QWebSocket()

            # Connect signals
            self.websocket.connected.connect(self.on_connected)
            self.websocket.disconnected.connect(self.on_disconnected)
            self.websocket.textMessageReceived.connect(self.on_message_received)

            self.initialized = True  # Mark as initialized

    def start_connection(self):
        '''
        Initiates the WebSocket connection
        '''
        self.websocket.open(self.url)

    def disconnect(self):
        '''
        Closes the WebSocket connection
        '''
        self.websocket.close()

    def send_message(self, message: str):
        '''
        Sends a message over the WebSocket connection
        '''
        if self.websocket.isValid():
            self.websocket.sendTextMessage(message)

    def on_connected(self):
        '''
        Handles WebSocket connection establishment
        '''
        self.connected.emit()

    def on_disconnected(self):
        '''
        Handles WebSocket disconnection
        '''
        self.disconnected.emit()

    def on_message_received(self, message: str):
        '''
        Handles received messages
        '''
        self.message_received.emit(message)

    def signal_handler(self, sig, frame):
        '''
        Handle termination from Ctrl+C
        '''
        print('Exiting...')
        self.disconnect()
        QCoreApplication.quit()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    def on_message(message: str):
        print(f"Received message: {message}")

    app = QApplication(sys.argv)
    # Enable terminating the application with Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    ws_client = WebSocketClient("wss://echo.websocket.events")

    # Connect signals
    ws_client.message_received.connect(on_message)

    # Connect and send a message
    ws_client.start_connection()
    ws_client.send_message("Hello, WebSocket!")

    app.exec()

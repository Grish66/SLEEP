import sys, asyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from qasync import QEventLoop, asyncSlot
import httpx

API_BASE = "http://127.0.0.1:8000"

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLEEP")
        self.label = QLabel("Click to check API health")
        self.btn = QPushButton("Ping /healthz")
        self.btn.clicked.connect(self.on_click)
        lay = QVBoxLayout(self)
        lay.addWidget(self.label)
        lay.addWidget(self.btn)

    @asyncSlot()
    async def on_click(self):
        try:
            async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
                r = await client.get("/healthz")
            self.label.setText(r.text)
        except Exception as e:
            self.label.setText(f"Error: {e}")

def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    w = Main()
    w.show()
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main()

import sys, asyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from qasync import QEventLoop, asyncSlot
import httpx
import keyring

from auth_ui import LoginDialog  # <-- import our dialog

API_BASE = "http://127.0.0.1:8000"
KEYRING_SERVICE = "SLEEP"

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLEEP")
        self.current_email: str | None = None

        # UI
        self.lbl_status = QLabel("Not logged in")
        self.btn_login = QPushButton("Login…")
        self.btn_ping = QPushButton("Ping /healthz")

        # layout
        row = QHBoxLayout()
        row.addWidget(self.btn_login)
        row.addWidget(self.btn_ping)
        lay = QVBoxLayout(self)
        lay.addWidget(self.lbl_status)
        lay.addLayout(row)

        # signals
        self.btn_login.clicked.connect(self.on_login_clicked)
        self.btn_ping.clicked.connect(self.on_ping_clicked)

    @asyncSlot()
    async def on_ping_clicked(self):
        try:
            self.lbl_status.setText("Pinging /healthz…")
            async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
                r = await client.get("/healthz")
            self.lbl_status.setText(r.text)
        except Exception as e:
            self.lbl_status.setText(f"Error: {e}")

    @asyncSlot()
    async def on_login_clicked(self):
        dlg = LoginDialog(self, api_base=API_BASE)
        if dlg.exec():  # dialog accepted
            # The dialog stores tokens in keyring; we just remember the email
            email = dlg.ed_email.text().strip()
            self.current_email = email
            # sanity check: make sure a token exists for this email
            has_access = bool(keyring.get_password(KEYRING_SERVICE, f"{email}:access"))
            self.lbl_status.setText(f"Logged in as {email} (token: {'ok' if has_access else 'missing'})")
        else:
            self.lbl_status.setText("Login canceled")

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

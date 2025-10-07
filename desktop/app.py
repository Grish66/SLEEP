import sys, asyncio
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from qasync import QEventLoop, asyncSlot
import httpx
import keyring

from auth_ui import LoginDialog
from auth_client import get_me
from notes_client import list_notes
from note_ui import NoteDialog  # <-- new

API_BASE = "http://127.0.0.1:8000"
KEYRING_SERVICE = "SLEEP"

class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SLEEP")
        self.current_email: str | None = None

        self.lbl_status = QLabel("Not logged in")
        self.btn_login  = QPushButton("Login…")
        self.btn_ping   = QPushButton("Ping /healthz")
        self.btn_me     = QPushButton("Who am I?")
        self.btn_notes  = QPushButton("List Notes")
        self.btn_new    = QPushButton("New Note…")  # <-- new

        row = QHBoxLayout()
        for b in (self.btn_login, self.btn_ping, self.btn_me, self.btn_notes, self.btn_new):
            row.addWidget(b)
        lay = QVBoxLayout(self)
        lay.addWidget(self.lbl_status)
        lay.addLayout(row)

        self.btn_login.clicked.connect(self.on_login_clicked)
        self.btn_ping.clicked.connect(self.on_ping_clicked)
        self.btn_me.clicked.connect(self.on_me_clicked)
        self.btn_notes.clicked.connect(self.on_notes_clicked)
        self.btn_new.clicked.connect(self.on_new_clicked)  # <-- new

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
        if dlg.exec():
            email = dlg.ed_email.text().strip()
            self.current_email = email
            has_access = bool(keyring.get_password(KEYRING_SERVICE, f"{email}:access"))
            self.lbl_status.setText(f"Logged in as {email} (token: {'ok' if has_access else 'missing'})")
        else:
            self.lbl_status.setText("Login canceled")

    @asyncSlot()
    async def on_me_clicked(self):
        if not self.current_email:
            self.lbl_status.setText("Please login first.")
            return
        from auth_client import get_me
        try:
            self.lbl_status.setText("Fetching /me…")
            data = await get_me(self.current_email)
            self.lbl_status.setText(f"/me → user_id={data.get('user_id')} email={data.get('email')}")
        except Exception as e:
            self.lbl_status.setText(f"/me error: {e}")

    @asyncSlot()
    async def on_notes_clicked(self):
        if not self.current_email:
            self.lbl_status.setText("Please login first.")
            return
        try:
            self.lbl_status.setText("Loading notes…")
            notes = await list_notes(self.current_email)
            titles = [n.get("title", "(no title)") for n in notes]
            summary = ", ".join(titles[:3]) + ("…" if len(titles) > 3 else "")
            self.lbl_status.setText(f"{len(notes)} note(s): {summary or '(none)'}")
        except Exception as e:
            self.lbl_status.setText(f"/notes error: {e}")

    @asyncSlot()
    async def on_new_clicked(self):
        if not self.current_email:
            self.lbl_status.setText("Please login first.")
            return
        dlg = NoteDialog(self, current_email=self.current_email)
        if dlg.exec():
            # After creating, refresh the summary
            try:
                notes = await list_notes(self.current_email)
                self.lbl_status.setText(f"Created. You now have {len(notes)} note(s).")
            except Exception as e:
                self.lbl_status.setText(f"Created, but list failed: {e}")
        else:
            self.lbl_status.setText("Create note canceled")

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

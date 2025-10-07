import sys, asyncio
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QCheckBox, QHBoxLayout, QPushButton, QApplication
from qasync import QEventLoop, asyncSlot
from typing import Optional

from notes_client import create_note

class NoteDialog(QDialog):
    """
    Minimal dialog to create a note:
      - title (QLineEdit)
      - body (QTextEdit)
      - done (QCheckBox)
    Calls backend on Save.
    """
    def __init__(self, parent=None, current_email: Optional[str] = None):
        super().__init__(parent)
        self.setWindowTitle("New Note")
        self.current_email = current_email

        self.lbl_status = QLabel("Enter note details")
        self.ed_title = QLineEdit()
        self.ed_title.setPlaceholderText("Title (required, max 200 chars)")
        self.ed_body = QTextEdit()
        self.chk_done = QCheckBox("Mark as done")

        self.btn_save = QPushButton("Save")
        self.btn_cancel = QPushButton("Cancel")

        lay = QVBoxLayout(self)
        lay.addWidget(self.lbl_status)
        lay.addWidget(self.ed_title)
        lay.addWidget(self.ed_body)
        lay.addWidget(self.chk_done)

        row = QHBoxLayout()
        row.addWidget(self.btn_save)
        row.addWidget(self.btn_cancel)
        lay.addLayout(row)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save.clicked.connect(self.on_save_clicked)

    def _set_busy(self, busy: bool):
        for w in (self.ed_title, self.ed_body, self.chk_done, self.btn_save, self.btn_cancel):
            w.setDisabled(busy)

    @asyncSlot()
    async def on_save_clicked(self):
        title = self.ed_title.text().strip()
        body = self.ed_body.toPlainText()
        done = self.chk_done.isChecked()

        if not self.current_email:
            self.lbl_status.setText("Please login first.")
            return
        if not title:
            self.lbl_status.setText("Title is required.")
            return
        if len(title) > 200:
            self.lbl_status.setText("Title too long (max 200).")
            return

        self._set_busy(True)
        self.lbl_status.setText("Saving…")
        try:
            note = await create_note(self.current_email, title, body, done)
            self.lbl_status.setText(f"Saved (id={note.get('id')})")
            self.accept()
        except Exception as e:
            self.lbl_status.setText(f"Error: {e}")
            self._set_busy(False)


# Standalone test (optional)
def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    import qasync, httpx  # noqa: F401 (ensure deps are present)
    from auth_ui import LoginDialog

    # quick flow: prompt login, then open NoteDialog
    dlg_login = LoginDialog()
    if dlg_login.exec():
        email = dlg_login.ed_email.text().strip()
        dlg_note = NoteDialog(current_email=email)
        with loop:
            dlg_note.show()
            loop.run_forever()
    else:
        print("Login canceled")

if __name__ == "__main__":
    main()

import os
import shutil
import signal
import socket
import subprocess
import time
from pathlib import Path

PORT = 9222
PROFILE = os.getenv("CHROME_PROFILE", str(Path.home() / "upwork_chrome_profile"))
DROP_ENV = ("GSETTINGS_SCHEMA_DIR", "GTK_PATH", "GIO_MODULE_DIR")


def port_open():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


class ChromeSession:
    """Піднімає Chrome з портом налагодження, якщо він ще не запущений."""

    def __enter__(self):
        self.proc = None
        if port_open():          # Chrome вже працює, нічого не чіпаємо
            return self

        env = {k: v for k, v in os.environ.items() if k not in DROP_ENV}
        cmd = [
            "google-chrome",
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={PROFILE}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        if os.geteuid() == 0:    # на сервері під root потрібен цей прапорець
            cmd.append("--no-sandbox")
        if not env.get("DISPLAY"):
            if shutil.which("xvfb-run"):
                cmd = ["xvfb-run", "-a", "--server-args=-screen 0 1440x900x24"] + cmd
            else:
                cmd.append("--headless=new")

        for f in Path(PROFILE).glob("Singleton*"):
            try:
                f.unlink()
            except OSError:
                pass

        self.proc = subprocess.Popen(
            cmd, env=env, start_new_session=True,
            stdout=subprocess.DEVNULL, stderr=None,
        )
        for _ in range(60):
            if port_open():
                return self
            time.sleep(0.5)
        self.__exit__()
        raise RuntimeError("Chrome не запустився за 30 секунд")

    def __exit__(self, *exc):
        if self.proc:
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
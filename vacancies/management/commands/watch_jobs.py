import random
import time
import traceback

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Запускає fetch_jobs по колу, поки не зупиниш (Ctrl+C)"

    def add_arguments(self, parser):
        parser.add_argument("--every", type=int, default=15, help="інтервал, хвилини")

    def handle(self, *args, **opts):
        base = opts["every"] * 60
        while True:
            try:
                call_command("fetch_jobs")
            except Exception:
                traceback.print_exc()
            pause = max(base + random.randint(-120, 120), 300)
            self.stdout.write(f"Наступний запуск через {pause // 60} хв")
            time.sleep(pause)
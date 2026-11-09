from django.core.management.base import BaseCommand

from vacancies.scraper import scrape


class Command(BaseCommand):
    help = "Разовий великий збір: гортає, поки не набере --max вакансій"

    def add_arguments(self, parser):
        parser.add_argument("--max", type=int, default=250)
        parser.add_argument("--max-scrolls", type=int, default=80)
        parser.add_argument("--debug", action="store_true",
                            help="показувати, які запити підвантажують вакансії")

    def handle(self, *args, **opts):
        r = scrape(max_jobs=opts["max"], stop_on_known=False,
                   max_scrolls=opts["max_scrolls"], debug=opts["debug"],
                   log=self.stdout.write)
        self.stdout.write(f"Відповіді: {r['aliases']}")
        self.stdout.write(self.style.SUCCESS(
            f"Зібрано: {r['total']}, нових: {r['created']}, оновлено: {r['updated']}"
        ))
from django.core.management.base import BaseCommand

from vacancies.scraper import scrape


class Command(BaseCommand):
    help = "Швидкий прохід: забирає лише нові вакансії (зупиняється на відомих)"

    def add_arguments(self, parser):
        parser.add_argument("--max", type=int, default=50)

    def handle(self, *args, **opts):
        r = scrape(max_jobs=opts["max"], stop_on_known=True, max_scrolls=10,
                   log=self.stdout.write)
        self.stdout.write(f"Відповіді: {r['aliases']}")
        self.stdout.write(self.style.SUCCESS(
            f"Зібрано: {r['total']}, нових: {r['created']}, оновлено: {r['updated']}"
        ))
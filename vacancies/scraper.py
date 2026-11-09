import json
import random
import re
from collections import Counter

from django.utils.dateparse import parse_datetime
from playwright.sync_api import sync_playwright

from vacancies.chrome import ChromeSession
from vacancies.models import Vacancy

CDP_URL = "http://localhost:9222"
FEED_URL = "https://www.upwork.com/nx/find-work/most-recent"


def find_jobs(o):
    if isinstance(o, dict):
        if "ciphertext" in o and "title" in o:
            yield o
        for v in o.values():
            yield from find_jobs(v)
    elif isinstance(o, list):
        for v in o:
            yield from find_jobs(v)


def make_budget(job):
    amount = (job.get("amount") or {}).get("amount") or 0
    hb = job.get("hourlyBudget") or {}
    if amount:
        return f"${amount:g} fixed"
    if hb.get("max"):
        return f"${hb.get('min', 0):g}-${hb['max']:g}/hr"
    return ""


def save_job(cipher, job):
    client = job.get("client") or {}
    _, created = Vacancy.objects.update_or_create(
        external_id=cipher,
        defaults={
            "title": job.get("title", "")[:500],
            "description": job.get("description", ""),
            "url": f"https://www.upwork.com/jobs/{cipher}",
            "budget": make_budget(job),
            "job_type": job.get("type"),
            "duration": job.get("durationLabel") or job.get("duration") or "",
            "engagement": job.get("engagement") or "",
            "tier": job.get("tier") or "",
            "proposals_tier": job.get("proposalsTier") or "",
            "skills": [a.get("prettyName") for a in job.get("attrs", [])],
            "client_country": (client.get("location") or {}).get("country", ""),
            "client_total_spent": client.get("totalSpent"),
            "client_payment_status": client.get("paymentVerificationStatus"),
            "published_at": parse_datetime(job["publishedOn"]) if job.get("publishedOn") else None,
        },
    )
    return created


def scrape(max_jobs, stop_on_known, max_scrolls, debug=False, log=print):
    known = set(Vacancy.objects.values_list("external_id", flat=True))
    collected = {}
    aliases = Counter()
    state = {"reached_known": False}

    def on_response(resp):
        if "/api/graphql/v1" not in resp.url:
            return
        try:
            jobs = list(find_jobs(resp.json()))
        except Exception:
            return
        if not jobs:
            return
        alias = resp.url.split("alias=")[-1] if "alias=" in resp.url else "?"
        aliases[alias] += 1
        if debug:
            # лише variables запиту (токени сидять у заголовках, сюди вони не потрапляють)
            try:
                variables = json.loads(resp.request.post_data or "{}").get("variables")
                log(f"[debug] {alias}: +{len(jobs)} вакансій, variables={json.dumps(variables)[:400]}")
            except Exception:
                log(f"[debug] {alias}: +{len(jobs)} вакансій")
        for j in jobs:
            c = j["ciphertext"]
            if c not in collected:
                collected[c] = j
                if c in known:
                    state["reached_known"] = True

    try:
        with ChromeSession():
            with sync_playwright() as p:
                browser = p.chromium.connect_over_cdp(CDP_URL)
                page = browser.contexts[0].new_page()
                page.on("response", on_response)
                try:
                    page.goto(FEED_URL)
                    page.wait_for_timeout(6000)
                    page.mouse.move(700, 500)

                    idle = 0
                    for i in range(max_scrolls):
                        if len(collected) >= max_jobs:
                            break
                        if stop_on_known and state["reached_known"]:
                            break

                        before = len(collected)
                        page.keyboard.press("End")
                        page.mouse.wheel(0, 5000)
                        try:
                            btn = page.get_by_role("button", name=re.compile("load more|show more", re.I))
                            if btn.count():
                                btn.first.click(timeout=2000)
                        except Exception:
                            pass
                        page.wait_for_timeout(random.randint(2500, 4500))

                        log(f"прокрутка {i + 1}: зібрано {len(collected)}")
                        idle = idle + 1 if len(collected) == before else 0
                        if idle >= 4:
                            log("нових вакансій більше не підвантажується")
                            break
                finally:
                    page.close()
    finally:
        # зберігаємо все, що встигли зібрати, навіть якщо щось впало
        jobs = list(collected.items())[:max_jobs]
        created = sum(save_job(c, j) for c, j in jobs)

    return {
        "total": len(jobs),
        "created": created,
        "updated": len(jobs) - created,
        "reached_known": state["reached_known"],
        "aliases": dict(aliases),
    }
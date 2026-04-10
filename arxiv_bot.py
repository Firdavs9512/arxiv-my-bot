"""
arXiv Daily Bot
---------------
Har kuni belgilangan arXiv kategoriyalaridan so'nggi 24 soat ichida
chiqqan yangi maqolalarni oladi va Telegram'ga yuboradi.
"""

import os
import sys
import html
import time
from datetime import datetime, timedelta, timezone

import arxiv
import requests

# ============ SOZLAMALAR ============

# Kuzatiladigan kategoriyalar
CATEGORIES = ["q-bio.NC", "cs.NE", "cs.LG"]

# Har bir kategoriyadan eng ko'pi bilan necha maqola tekshiriladi
# (filtrlashdan oldin). Yangi maqolalar odatda kuniga 50-200 ta bo'ladi.
MAX_FETCH_PER_CATEGORY = 200

# Necha soatlik maqolalar "yangi" hisoblanadi
LOOKBACK_HOURS = 26  # 24 emas, balki 26 — kichik kechikishlarni qoplash uchun

# Telegram'ga yuborishda eng ko'pi bilan necha maqola yuboriladi
# (juda ko'p bo'lib ketmasligi uchun)
MAX_SEND_PER_CATEGORY = 15

# Telegram sozlamalari (GitHub Secrets'dan olinadi)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Telegram API URL
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ============ ARXIV FUNKSIYALARI ============


def fetch_recent_papers(category: str) -> list:
    """
    Berilgan kategoriyadan so'nggi 26 soat ichida chiqqan maqolalarni oladi.
    Maqolalar yangi yuborilgan vaqti bo'yicha tartiblanadi.
    """
    client = arxiv.Client(
        page_size=100,
        delay_seconds=3,  # arXiv API'ga hurmat bilan
        num_retries=3,
    )

    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=MAX_FETCH_PER_CATEGORY,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    recent = []

    try:
        for result in client.results(search):
            # Maqolaning yuborilgan vaqti cutoff'dan eski bo'lsa, to'xtatamiz
            # (chunki natijalar vaqt bo'yicha kamayish tartibida)
            if result.published < cutoff:
                break
            recent.append(result)
    except Exception as e:
        print(f"  ⚠️  {category} uchun xato: {e}", file=sys.stderr)

    return recent


# ============ TELEGRAM FUNKSIYALARI ============


def escape_html(text: str) -> str:
    """HTML maxsus belgilarini ekranlash."""
    return html.escape(text or "", quote=False)


def format_paper(paper) -> str:
    """Bitta maqolani Telegram uchun HTML formatda tayyorlash."""
    title = escape_html(paper.title.strip().replace("\n", " "))

    # Mualliflar — eng ko'pi bilan 4 ta, qolganlari "et al."
    authors_list = [a.name for a in paper.authors]
    if len(authors_list) > 4:
        authors_str = ", ".join(authors_list[:4]) + f", et al. ({len(authors_list)} mualliflar)"
    else:
        authors_str = ", ".join(authors_list)
    authors = escape_html(authors_str)

    # Abstract — uzun bo'lsa, qisqartiramiz
    abstract = paper.summary.strip().replace("\n", " ")
    if len(abstract) > 600:
        abstract = abstract[:600].rsplit(" ", 1)[0] + "..."
    abstract = escape_html(abstract)

    # Kategoriyalar
    categories = ", ".join(paper.categories[:3])
    categories = escape_html(categories)

    # Yuborilgan sana
    published = paper.published.strftime("%Y-%m-%d %H:%M UTC")

    # PDF va abs URL
    pdf_url = paper.pdf_url
    abs_url = paper.entry_id  # bu abstract sahifasiga link

    message = (
        f"📄 <b>{title}</b>\n\n"
        f"👥 <i>{authors}</i>\n\n"
        f"📝 {abstract}\n\n"
        f"🏷 {categories}\n"
        f"📅 {published}\n\n"
        f'🔗 <a href="{abs_url}">Abstract</a> | <a href="{pdf_url}">PDF</a>'
    )

    return message


def send_telegram_message(text: str, retries: int = 3) -> bool:
    """Telegram'ga xabar yuborish."""
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    for attempt in range(retries):
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return True
            elif response.status_code == 429:
                # Rate limit — kutib ko'rib qayta urinamiz
                retry_after = response.json().get("parameters", {}).get("retry_after", 5)
                print(f"  ⏳ Rate limit, {retry_after}s kutamiz...", file=sys.stderr)
                time.sleep(retry_after + 1)
            else:
                print(
                    f"  ❌ Telegram xato {response.status_code}: {response.text[:200]}",
                    file=sys.stderr,
                )
                return False
        except requests.RequestException as e:
            print(f"  ⚠️  So'rov xatosi: {e}", file=sys.stderr)
            time.sleep(2)

    return False


# ============ ASOSIY ISH ============


def main():
    # Sozlamalar tekshiruvi
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Xato: TELEGRAM_BOT_TOKEN yoki TELEGRAM_CHAT_ID o'rnatilmagan!")
        sys.exit(1)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"🚀 arXiv bot ishga tushdi — {today}")

    # Sarlavha xabari
    header = (
        f"🌅 <b>arXiv kunlik yangiliklar</b>\n"
        f"📅 {today}\n"
        f"🏷 Kategoriyalar: {', '.join(CATEGORIES)}\n\n"
        f"<i>So'nggi {LOOKBACK_HOURS} soat ichidagi yangi maqolalar 👇</i>"
    )
    send_telegram_message(header)
    time.sleep(1)

    total_sent = 0

    for category in CATEGORIES:
        print(f"\n📂 {category} tekshirilmoqda...")
        papers = fetch_recent_papers(category)

        if not papers:
            print(f"  ℹ️  Yangi maqola topilmadi")
            send_telegram_message(
                f"📂 <b>{escape_html(category)}</b>\n<i>Yangi maqola yo'q</i>"
            )
            time.sleep(1)
            continue

        # Eng ko'pi bilan MAX_SEND_PER_CATEGORY ta yuboramiz
        papers_to_send = papers[:MAX_SEND_PER_CATEGORY]
        truncated = len(papers) > MAX_SEND_PER_CATEGORY

        # Kategoriya sarlavhasi
        cat_header = (
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📂 <b>{escape_html(category)}</b>\n"
            f"📊 Topildi: {len(papers)} ta"
        )
        if truncated:
            cat_header += f" (eng yangi {MAX_SEND_PER_CATEGORY} tasi yuborilmoqda)"
        cat_header += "\n━━━━━━━━━━━━━━━━━━━"

        send_telegram_message(cat_header)
        time.sleep(1)

        # Har bir maqolani yuborish
        for i, paper in enumerate(papers_to_send, 1):
            message = format_paper(paper)
            success = send_telegram_message(message)
            if success:
                total_sent += 1
                print(f"  ✅ [{i}/{len(papers_to_send)}] {paper.title[:60]}...")
            else:
                print(f"  ❌ [{i}/{len(papers_to_send)}] Yuborilmadi")

            # Telegram rate limit'ga tushib qolmaslik uchun
            time.sleep(1.5)

    # Yakuniy xabar
    footer = (
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Yakunlandi</b>\n"
        f"📨 Jami yuborildi: {total_sent} ta maqola\n"
        f"🔄 Keyingi yangilanish: ertaga ertalab"
    )
    send_telegram_message(footer)
    print(f"\n✅ Tugadi! Jami: {total_sent} ta maqola yuborildi")


if __name__ == "__main__":
    main()

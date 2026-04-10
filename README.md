# 📚 arXiv Daily Bot

Har kuni ertalab Telegram'ga sevimli arXiv kategoriyalaringizdan yangi maqolalarni yuboradigan bot. GitHub Actions'da bepul ishlaydi — server kerak emas.

## ✨ Xususiyatlar

- 🕗 Har kuni Turkiya vaqti bilan ertalab **08:00** da avtomatik ishga tushadi
- 📂 3 ta kategoriyani kuzatadi: `q-bio.NC`, `cs.NE`, `cs.LG`
- 📨 Telegram'ga go'zal HTML formatda yuboradi (sarlavha, mualliflar, abstract, PDF havolasi)
- 💸 To'liq **bepul** (GitHub Actions free tier'dan foydalanadi)
- 🔧 Oson sozlanadi va kengaytiriladi

## 🚀 Sozlash bosqichlari

### 1-qadam: Telegram bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Botingizga ism bering (masalan: `My arXiv Bot`)
4. Username bering (masalan: `my_arxiv_papers_bot`) — `_bot` bilan tugashi shart
5. BotFather sizga **token** beradi, masalan: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
6. **Bu tokenni saqlang** — keyinroq kerak bo'ladi

### 2-qadam: Chat ID'ni olish

1. Yangi yaratgan botingizni Telegram'da toping va `/start` bosing (yoki shunchaki "Salom" deb yozing)
2. Brauzeringizda quyidagi manzilga o'ting (TOKEN o'rniga o'z tokeningizni qo'ying):
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
3. JSON javobida `"chat":{"id":123456789,...` ni toping
4. Bu **123456789** sizning Chat ID'ngiz — saqlang

### 3-qadam: GitHub repository yaratish

1. [github.com](https://github.com) ga kiring
2. **New repository** tugmasini bosing
3. Nom bering, masalan: `arxiv-daily-bot`
4. **Private** yoki **Public** — farqi yo'q (Public bo'lsa ham token xavfsiz, chunki Secrets'da saqlanadi)
5. **Create repository** bosing

### 4-qadam: Fayllarni yuklash

Quyidagi fayllarni repository'ga yuklang (xuddi shu strukturada):

```
arxiv-daily-bot/
├── arxiv_bot.py
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
        └── daily.yml
```

**Eng oson yo'l — GitHub web interfeysi orqali:**

1. Repository sahifasida **Add file → Upload files** ni bosing
2. `arxiv_bot.py` va `requirements.txt` fayllarini sudrab tashlang
3. **Commit changes** ni bosing
4. Keyin **Add file → Create new file** ni bosing
5. Fayl nomi joyiga: `.github/workflows/daily.yml` deb yozing (slash'lar bilan — bu papka yaratadi)
6. Ichiga `daily.yml` faylining mazmunini joylashtiring
7. **Commit new file** bosing

### 5-qadam: GitHub Secrets sozlash

Bu eng muhim qadam — token va chat ID'ni xavfsiz saqlash uchun.

1. Repository sahifasida **Settings** ga o'ting
2. Chap menyudan **Secrets and variables → Actions** ni tanlang
3. **New repository secret** tugmasini bosing
4. Birinchi secret:
   - **Name:** `TELEGRAM_BOT_TOKEN`
   - **Secret:** BotFather bergan tokeningiz (masalan: `123456789:ABCdef...`)
   - **Add secret** bosing
5. Yana **New repository secret** ni bosing
6. Ikkinchi secret:
   - **Name:** `TELEGRAM_CHAT_ID`
   - **Secret:** Chat ID'ngiz (masalan: `123456789`)
   - **Add secret** bosing

### 6-qadam: Sinab ko'rish

Avtomatik ishga tushishni kutmasdan, qo'lda sinab ko'ring:

1. Repository'da **Actions** bo'limiga o'ting
2. Chap tarafda **arXiv Daily Bot** ni tanlang
3. O'ng tomonda **Run workflow → Run workflow** tugmasini bosing
4. Bir necha daqiqa kuting (odatda 1-2 daqiqa)
5. Telegram'ingizga xabarlar kelishi kerak! 🎉

Agar xato bo'lsa, **Actions** bo'limidagi ishga tushirilgan workflow'ni bosing va loglarni ko'ring.

## ⚙️ Sozlamalarni o'zgartirish

`arxiv_bot.py` faylining yuqorisida sozlamalar bor:

```python
# Kuzatiladigan kategoriyalar
CATEGORIES = ["q-bio.NC", "cs.NE", "cs.LG"]

# Necha soatlik maqolalar "yangi" hisoblanadi
LOOKBACK_HOURS = 26

# Telegram'ga eng ko'pi bilan necha maqola yuboriladi
MAX_SEND_PER_CATEGORY = 15
```

### Boshqa kategoriyalar qo'shish

Mashhur AI/ML kategoriyalari:
- `cs.AI` — Artificial Intelligence
- `cs.CV` — Computer Vision
- `cs.CL` — Computation and Language (NLP)
- `stat.ML` — Statistics / Machine Learning
- `q-bio.NC` — Neurons and Cognition
- `cs.NE` — Neural and Evolutionary Computing
- `cs.LG` — Machine Learning

To'liq ro'yxat: [arxiv.org/category_taxonomy](https://arxiv.org/category_taxonomy)

### Vaqtni o'zgartirish

`.github/workflows/daily.yml` faylida:

```yaml
- cron: '0 5 * * *'  # UTC 05:00 = Turkiya 08:00
```

Cron format: `daqiqa soat * * *`

Misollar (Turkiya vaqti, UTC+3):
- Ertalab 07:00 → `cron: '0 4 * * *'`
- Ertalab 09:00 → `cron: '0 6 * * *'`
- Kechqurun 18:00 → `cron: '0 15 * * *'`

⚠️ **Eslatma:** GitHub Actions schedule biroz kechikishi mumkin (5-15 daqiqa). Bu normal holat.

## 🐛 Muammolarni hal qilish

**"Telegram xato 401"** — Token noto'g'ri. Secrets'ni qaytadan tekshiring.

**"Telegram xato 400: chat not found"** — Chat ID noto'g'ri yoki botga `/start` bosmagansiz.

**"Yangi maqola yo'q"** — Bu normal. Ba'zi kunlari yangi maqola kam bo'lishi mumkin (ayniqsa dam olish kunlari).

**Workflow ishga tushmayapti** — GitHub Actions ba'zan kechikadi. Agar 30 daqiqadan keyin ham ishlamasa, qo'lda **Run workflow** orqali sinab ko'ring.

## 📝 Litsenziya

Erkin foydalaning! O'zingiz uchun moslang va kerak bo'lsa do'stlaringizga ulashing.

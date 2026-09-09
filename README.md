# 👷‍♂️ Bosh Muhandis va Bosh Smetachi Telegram Boti

50 yillik amaliy tajribaga ega faxriy bosh muhandis, quruvchi va bosh smetachi (ShNQ, QMQ, SNiP hamda amaldagi bozor narxlari bo'yicha mutaxassis) shaxsiyatiga ega professional Telegram bot.

---

## 🎯 Botning asosiy vazifalari va imkoniyatlari

1. **📋 Oferta (Tijorat taklifi) tayyorlash:**
   - Pudratchi yoki buyurtmachi uchun texnik va yuridik jihatdan puxta tuzilgan rasmiy takliflar;
   - Aniq bajarilish muddatlari, bosqichma-bosqich to'lov rejalari (avans, oraliq va yakuniy);
   - Tomonlarning javobgarlik chegaralari, kafolat muddatlari va penya shartlari.

2. **📐 Texnik topshiriq (TZ) hisob-kitoblari:**
   - Ob'ekt hajmidan kelib chiqib asosiy va yordamchi materiallar sarfi;
   - Ishchi kuchi me'yoriy sarfi (odam-soat);
   - Mashina va mexanizmlar zaruriyati (mashina-soat);
   - Qurilish-montaj ishlarining texnologik ketma-ketligi va xavfsizlik qoidalari.

3. **📑 Qurilish hujjatlari va davlat standart formalari:**
   - **Forma-2:** Bajarilgan ishlar dalolatnomasi (KC-2);
   - **Forma-3:** Mahalliy smeta / sarf-xarajat ma'lumotnomasi (KC-3);
   - **Defekt dalolatnomasi:** Nuqsonlar va zaruriy ta'mirlash choralari ro'yxati;
   - **M-29 hisoboti:** Materiallarni sarf me'yori bo'yicha hisobdan chiqarish akti.
   - Barcha hujjatlar to'g'ridan-to'g'ri nusxa olib, rasmiy ish yuritishda foydalanishga tayyor shaklda beriladi.

4. **🧱 Standartlarga asoslangan Smeta:**
   - O'zbekiston shaharsozlik normalari (**ShNQ**) va **SNiP** talablariga qat'iy rioya;
   - Materiallarning texnologik isrof (**otxod**) me'yorlarini hisobga olish (gipsokarton 3-5%, kafel 7-10%, g'isht 2-3%, qorishmalar 3-5% va h.k.);
   - Narxlarni O'zbekiston sharoitida (so'mda) yoki xalqaro sharoitda (AQSH dollarida) hisoblash;
   - Smetalar faqat ixcham Markdown jadvallarida:
     `| № | Ish/Material nomi | O'lchov birligi | Miqdori (so'm/dollar) | Birlik narxi | Jami |`

5. **🎖 Faxriy muhandis xulosasi:**
   - Har bir javob yakunida: *"Mening 50 yillik amaliyotim shuni ko'rsatadiki..."* iborasi bilan yashirin xatarlar (qishki koeffitsient, qotish texnologik vaqti, namlik, yashirin ishlar dalolatnomasi, 5-10% kutilmagan rezerv xarajatlar) bo'yicha professional ogohlantirishlar beriladi.

---

## 📂 Loyiha tuzilishi

```text
smeta/
├── .env                  # Maxfiy tokenlar va API kalitlari
├── .env.example          # Namuna sozlama fayli
├── ai_service.py         # Gemini va OpenAI bilan ishlovchi AI xizmati + xotira boshqaruvi
├── config.py             # Sozlamalarni yuklovchi va tekshiruvchi modul
├── handlers.py           # Telegram xabarlari, buyruqlari va tugmalar mantiqi
├── keyboards.py          # Menyu va valyuta tanlash klaviaturalari
├── main.py               # Botni ishga tushiruvchi asosiy fayl
├── prompts.py            # Bosh muhandis tizim prompti va shablonlar
├── requirements.txt      # Kerakli Python kutubxonalari
└── README.md             # Qo'llanma
```

---

## 🚀 O'rnatish va ishga tushirish (Qadamma-qadam)

### 1-qadam: Virtual muhit (venv) yaratish va faollashtirish
Loyiha papkasida (`c:\Users\lenovo\Desktop\smeta`) terminalni oching:

```bash
# Windows PowerShell yoki CMD da:
python -m venv venv

# Faollashtirish:
venv\Scripts\activate
```

### 2-qadam: Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3-qadam: Telegram Bot Token olish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini yuboring va ko'rsatmalarga amal qilib bot yarating.
3. BotFather bergan HTTP API tokenni nusxalab oling (masalan: `7123456789:ABCdefGhIJK...`).

### 4-qadam: AI API Kalitini olish
Bot aqli sifatida **Google Gemini** (tavsiya etiladi, bepul va tez) yoki **OpenAI** dan foydalanishingiz mumkin:
- **Google Gemini API olish (bepul):**
  1. [Google AI Studio](https://aistudio.google.com/) saytiga kiring.
  2. Google hisobingiz orqali kiring va **"Get API key"** tugmasini bosing.
  3. API kalitingizni nusxalab oling.

### 5-qadam: `.env` faylini sozlash
Loyiha papkasidagi `.env` faylini oching va kalitlaringizni joylashtiring:

```env
BOT_TOKEN=7123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ_1234567
AI_PROVIDER=gemini
GEMINI_API_KEY=AIzaSySizningKalitingiz...
AI_MODEL=gemini-2.5-flash
MAX_HISTORY_MESSAGES=10
```

*(Agar OpenAI ishlatmoqchi bo'lsangiz: `AI_PROVIDER=openai`, `OPENAI_API_KEY=sk-...` qilib belgilang).*

### 6-qadam: Botni ishga tushirish
```bash
python main.py
```

Konsolda quyidagi xabarni ko'rasiz:
```text
[INFO] BoshMuhandisBot: Telegram buyruqlar menyusi o'rnatildi.
[INFO] BoshMuhandisBot: Bot tayyor va xabarlarni qabul qilmoqda...
```

---

## 💡 Namunaviy so'rovlar (Foydalanish misollari)

Telegram botingizga quyidagi so'rovlarni yuborib sinab ko'rishingiz mumkin:

1. **Qisman ma'lumot berilganda (aniqlashtirish mantiqi):**
   > *"Menga 100 kv.m suvoq qilish narxini hisoblab ber."*
   - Bot qatlam qalinligi, qorishma turi (gips yoki sement-qum), ichki yoki tashqi devor ekanligini hamda valyutani aniqlashtiradi. Agar foydalanuvchi "boridan hisoblayver" desa, ShNQ standarti bo'yicha (20 mm qatlam) hisoblab beradi.

2. **To'liq smeta tuzish:**
   > *"Toshkent shahrida 150 kv.m xonadonda qalinligi 50 mm li sement-qum (M-150) parda quyish (styajka) smetasi kerak. Narxlar so'mda bo'lsin."*
   - Bot sement, qum, plastifikator, setka va ish haqini otxod (3-5%) bilan birga hisoblab, to'liq jadval taqdim etadi.

3. **Oferta (Tijorat taklifi):**
   > *"Fasadni bazalt bilan izolyatsiya qilish va travertin suvoq surtish bo'yicha buyurtmachiga rasmiy Oferta tayyorlab ber. Ob'ekt hajmi: 400 kv.m, muddat: 25 kun."*

4. **Forma-2 va Forma-3:**
   > *"Toshkent shahar, Chilonzor tumanidagi 500 kv.m tom yopish (profnastil) ishlari yakunlangani bo'yicha Forma-2 dalolatnomasi tuzib ber."*

---

## 🛡 Xavfsizlik va barqarorlik
- **Telegram cheklovlari:** 4096 belgidan oshadigan yirik smetalar jadval va matn strukturasini buzmagan holda avtomatik ravishda alohida xabarlarga bo'lib yuboriladi.
- **Kontekst boshqaruvi:** Har bir foydalanuvchining hisob-kitob jarayoni xotirada saqlanadi, shuning uchun ketma-ket aniqlashtirishlar kontekstdan uzilib qolmaydi. Yangi hisob boshlash uchun `/clear` buyrug'i mavjud.

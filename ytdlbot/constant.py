#!/usr/local/bin/python3
# coding: utf-8

# ytdlbot - constant.py
# 8/16/21 16:59
#

__author__ = "Benny <benny.think@gmail.com>"

import os

from config import (
    AFD_LINK,
    COFFEE_LINK,
    ENABLE_CELERY,
    FREE_DOWNLOAD,
    REQUIRED_MEMBERSHIP,
    TOKEN_PRICE,
)
from database import InfluxDB
from utils import get_func_queue


class BotText:
    start = """
    YouTube İndirme botuna hoş geldiniz. Daha fazla bilgi için /help yazın. TR Botunu kullanmanızı öneririz. Güncellemeler için https://t.me/OfficiallKiyici 'ya Mesaj Atın."""

    help = """
1. YouTube ve yt-dlp tarafından desteklenen tüm web siteleri için bağlantıyı göndermeniz yeterli; biz de indirip size gönderelim..

2. Belirli bağlantılar için `/spdl {URL}` kullanın. Daha fazla bilgi için: @OfficiallKiyici

3. Bot çalışmıyorsa tekrar deneyin veya güncellemeler için https://t.me/Officiallkiyici 'ya Mesaj Atın..

4. Wanna deploy it yourself?\nHere's the source code: @Meyitzade
    """

    about = "GİTHUB REPO İÇİN @meyitzade"

    buy = f"""
**Şartlar:**
1. 24 saatlik süre içinde videoyu {FREE_DOWNLOAD} kez indirmek için bu botu kullanabilirsiniz.

2. Kalıcı olarak geçerli olan ek indirme jetonları satın alabilirsiniz.

3. Para iadesi mümkündür, ihtiyacınız olursa benimle iletişime geçin @OfficialKiyici

4. Ücretli kullanıcılar için indirme, sıraya girmeyi önlemek amacıyla otomatik olarak Yerel moda değiştirilecek.

5. Ücretli kullanıcı 2GB'tan büyük dosyaları indirebilir.

**Fiyat:**
kalıcı olarak-
1. 1 USD == {TOKEN_PRICE} tokens
2. 7 CNY == {TOKEN_PRICE} tokens
3. 10 TRX == {TOKEN_PRICE} tokens

**Ödeme seçenekleri:**
İstediğiniz tutarı ödeyin. Örneğin, {TOKEN_PRICE * 2} token karşılığında 20 TRX gönderebilirsiniz.
1. AFDIAN(AliPay, WeChat Pay and PayPal): {AFD_LINK}
2. Buy me a coffee: {COFFEE_LINK}
3. Telegram Bot Payment(Stripe), please click Bot Payment button.
4. TRON(TRX), please click TRON(TRX) button.

**After payment:**
1. Afdian: attach order number with /redeem command (e.g., `/redeem 123456`).
2. Buy Me a Coffee: attach email with /redeem command (e.g., `/redeem 123@x.com`). **Use different email each time.**
3. Telegram Payment & Tron(TRX): automatically activated within 60s. Check /start to see your balance.

Want to buy more token with Telegram payment? Let's say 100? Here you go! `/buy 123`
    """

    private = "This bot is for private use"

    membership_require = f"You need to join this group or channel to use this bot\n\nhttps://t.me/{REQUIRED_MEMBERSHIP}"

    settings = """
Please choose the preferred format and video quality for your video. These settings only **apply to YouTube videos**.

High quality is recommended. Medium quality aims to 720P, while low quality is 480P.

If you choose to send the video as a document, it will not be possible to stream it.

Your current settings:
Video quality: **{0}**
Sending format: **{1}**
"""
    custom_text = os.getenv("CUSTOM_TEXT", "")

    premium_warning = """
    Your file is too big, do you want me to try to send it as premium user? 
    This is an experimental feature so you can only use it once per day.
    Also, the premium user will know who you are and what you are downloading. 
    You may be banned if you abuse this feature.
    """

    @staticmethod
    def get_receive_link_text() -> str:
        reserved = get_func_queue("reserved")
        if ENABLE_CELERY and reserved:
            text = f"Your tasks was added to the reserved queue {reserved}. Processing...\n\n"
        else:
            text = "Your task was added to active queue.\nProcessing...\n\n"

        return text

    @staticmethod
    def ping_worker() -> str:
        from tasks import app as celery_app

        workers = InfluxDB().extract_dashboard_data()
        # [{'celery@BennyのMBP': 'abc'}, {'celery@BennyのMBP': 'abc'}]
        response = celery_app.control.broadcast("ping_revision", reply=True)
        revision = {}
        for item in response:
            revision.update(item)

        text = ""
        for worker in workers:
            fields = worker["fields"]
            hostname = worker["tags"]["hostname"]
            status = {True: "✅"}.get(fields["status"], "❌")
            active = fields["active"]
            load = "{},{},{}".format(fields["load1"], fields["load5"], fields["load15"])
            rev = revision.get(hostname, "")
            text += f"{status}{hostname} **{active}** {load} {rev}\n"

        return text

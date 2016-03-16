#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import Updater
import telegram
import logging
from manager import manager
from datetime import datetime
from mods import logger_sys as log
from time import sleep
id_channel = -18779391
#id_channel = 84340477
id_priva = 84340477

man = manager()
#man.update_things()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

def packet(p,a):
    name = p.message.from_user.username
    id = p.message.chat_id
    text = p.message.text
    msg_id = p.message.message_id
    return {"name":name,"id":id,"text":text,"args":a, "msg_id": msg_id}

def get_print_time():
    return "%s:%s" % (datetime.now().hour, datetime.now().minute)

def brew(bot,update,args):
    p = packet(update,args)
    man.queue_coffee(p)
    print("%s - Brew %s" % (get_print_time(), p["name"]))

def brew_timer(bot):
    r = man.brew_timer()
    if r is not None:
        if r[2] is not None:
            bot.sendMessage(r[1], r[0], reply_to_message_id=r[2], parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            bot.sendMessage(r[1], r[0], parse_mode=telegram.ParseMode.MARKDOWN)

def brew_score(bot,update,args):
    p = packet(update,args)
    print("%s - Brew score %s" % (get_print_time(), p["name"]))
    man.brew_score(p)

def brew_stats(bot,update,args):
    p = packet(update, args)
    print("%s - Brew Stats %s" % (get_print_time(), p["name"]))
    man.brew_stats(p)

def brew_check(bot, update, args):
    p = packet(update,args)
    man.brew_check(p)

def brew_inventory(bot, update, args):
    p = packet(update,args)
    print("%s - Brew Inv %s" % (get_print_time(), p["name"]))
    man.brew_inventory(p)

def brew_cons(bot, update, args):
    p = packet(update, args)
    man.cons_use(p)
    print("%s - Cons use %s" % (get_print_time(), p["name"]))

def brew_help(bot, update, args):
    p = packet(update, args)
    text = "Brew 0.7 + Items&Drops DLC + ILLUMICOFFEE\n" \
           "ILLUMINATI aikoo tuhota maailman kahvipavut. Vain SINULLA on mahdollisuus estää tämä.\n" \
           "Komennot:\n" \
           "/illuminati\n" \
           "/illumi_shop\n" \
           "/give_money -name- -amount-"
    print("%s - Brew Help %s" % (get_print_time(), p["name"]))
    bot.sendMessage(p["id"], text)

def brew_status(bot, update, args):
    p = packet(update, args)
    r = man.brew_status()
    bot.sendMessage(p["id"], r, parse_mode=telegram.ParseMode.MARKDOWN)

def rahka(bot, update, args):
    p = packet(update, args)
    #r = man.brew_status()
    bot.sendMessage(p["id"], "[Items:](www.gmf.fi/blank)", parse_mode=telegram.ParseMode.MARKDOWN)

def illuminati(bot, update, args):
    p = packet(update, args)
    man.illumi_stats(p)
    print("%s - Illumi stats %s" % (get_print_time(), p["name"]))

def illumi_shop(bot, update, args):
    p = packet(update, args)
    man.illumi_shop(p)
    print("%s - Brew Stats %s" % (get_print_time(), p["name"]))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def give_money(bot, update, args):
    p = packet(update, args)
    print("%s - Brew Stats %s" % (get_print_time(), p["name"]))
    man.give_money(p)

def terasta(bot, update, args):
    p = packet(update, args)
    print(p["id"])
    bot.sendMessage(p["id"], "Terästit kahviasi koskenkorvalla.")

def brew_notify(bot, update, args):
    p = packet(update, args)
    man.brew_notify(p)

def brew_cancel(bot, update, args):
    p = packet(update, args)
    man.brew_cancel(p)

def farm_update(bot):
    man.farm_workers_update()

def farm_stats(bot, update, args):
    p = packet(update, args)
    r = man.farm_stats(p)
    bot.sendMessage(p["id"], r)

def msg_que(bot):
    man.illumi_time_check()
    if len(man.msg_que) != 0:
        for x in man.msg_que:
            id, msg = x[0], x[1]
            if msg is not None:
                if id is not None:
                    bot.sendMessage(id, msg, parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    bot.sendMessage(id_priva, msg, parse_mode=telegram.ParseMode.MARKDOWN)
        man.msg_que = []

def main():
    updater = Updater(man.settings["authkey"]) #brew bot
    #updater = Updater(man.settings["authkey_gmfrpg"]) #gmf rpg
    dp = updater.dispatcher
    j_que = updater.job_queue
    j_que.put(brew_timer, 1)
    j_que.put(msg_que, 2)
    j_que.put(farm_update, 30)
    print("Brew 0.80 + Items&Drops DLC 2.0 + ILLUMICOFFEE")

    dp.addTelegramCommandHandler("brew", brew)
    dp.addTelegramCommandHandler("brew_stats", brew_stats)
    dp.addTelegramCommandHandler("brew_score", brew_score)
    dp.addTelegramCommandHandler("brew_check", brew_check)
    dp.addTelegramCommandHandler("brew_inventory", brew_inventory)
    dp.addTelegramCommandHandler("brew_cons", brew_cons)
    dp.addTelegramCommandHandler("brew_help", brew_help)
    dp.addTelegramCommandHandler("brew_status", brew_status)
    dp.addTelegramCommandHandler("rahka", rahka)
    dp.addTelegramCommandHandler("illuminati", illuminati)
    dp.addTelegramCommandHandler("illumi_shop", illumi_shop)
    dp.addTelegramCommandHandler("give_money", give_money)
    dp.addTelegramCommandHandler("terästä", terasta)
    dp.addTelegramCommandHandler("brew_notify", brew_notify)
    dp.addTelegramCommandHandler("brew_cancel", brew_cancel)
    dp.addTelegramCommandHandler("farm_stats", farm_stats)
    #dp.addTelegramMessageHandler(forward_checker)

    dp.addErrorHandler(error)
    update_queue = updater.start_polling(poll_interval=2, timeout=10)

    while True:
        try:
            text = input()
        except NameError:
            text = input()

        # Gracefully stop the event handler
        if text == 'stop':
            updater.stop()
            break

        # else, put the text into the update queue to be handled by our handlers
        elif len(text) > 0:
            update_queue.put(text)

if __name__ == '__main__':
    main()


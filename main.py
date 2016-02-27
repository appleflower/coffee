#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import Updater
import telegram
import logging
from manager import manager
from datetime import datetime
from mods import logger_sys as log
from time import sleep
id_test = -116368010
id_priva = 84340477
man = manager()
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
    r = man.queue_coffee(p)
    print("%s - Brew %s" % (get_print_time(), p["name"]))
    bot.sendMessage(p["id"], r)
    log.log_command("Brew", p["name"], args)

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
    log.log_command("Brew Score", p["name"], args)
    bot.sendMessage(p["id"],man.brew_score(p["name"]), parse_mode=telegram.ParseMode.MARKDOWN)

def brew_stats(bot,update,args):
    p = packet(update, args)
    print("%s - Brew Stats %s" % (get_print_time(), p["name"]))
    log.log_command("Brew Stats", p["name"], args)
    bot.sendMessage(p["id"], man.brew_stats(p), parse_mode=telegram.ParseMode.MARKDOWN)

def brew_check(bot, update, args):
    p = packet(update,args)
    r = man.brew_check(p)
    log.log_command("Brew Check", p["name"], args)
    bot.sendMessage(p["id"], r)

def brew_inventory(bot, update, args):
    p = packet(update,args)
    print("%s - Brew Inv %s" % (get_print_time(), p["name"]))
    log.log_command("Brew Inv", p["name"], args)
    r = man.brew_inventory(p)
    bot.sendMessage(p["id"], r, parse_mode=telegram.ParseMode.MARKDOWN)

def brew_remove(bot, update, args):
    p = packet(update,args)
    r = man.item_remove(p)
    print("%s - Brew item remove %s" % (get_print_time(), p["name"]))
    log.log_command("Brew item remove", p["name"], args)
    bot.sendMessage(p["id"], r)

def brew_cons(bot, update, args):
    p = packet(update, args)
    r = man.cons_use(p)
    print("%s - Cons use %s" % (get_print_time(), p["name"]))
    log.log_command("Brew cons use", p["name"], args)
    bot.sendMessage(p["id"], r)

def brew_help(bot, update, args):
    p = packet(update, args)
    text = "Brew 0.7 + Items&Drops DLC + ILLUMICOFFEE\n" \
           "ILLUMINATI aikoo tuhota maailman kahvipavut. Vain SINULLA on mahdollisuus estää tämä.\n" \
           "Komennot:\n" \
           "/illuminati\n" \
           "/illumi_shop\n" \
           "/give_money -name- -amount-"
    print("%s - Brew Help %s" % (get_print_time(), p["name"]))
    log.log_command("Brew Help", p["name"], args)
    bot.sendMessage(p["id"], text)
    print(p["id"])

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
    r = man.illumi_stats(p)
    print("%s - Illumi stats %s" % (get_print_time(), p["name"]))
    log.log_command("Illuminati Stats", p["name"], args)
    bot.sendMessage(p["id"], r, parse_mode=telegram.ParseMode.MARKDOWN)

def illumi_shop(bot, update, args):
    p = packet(update, args)
    r = man.illumi_shop(p)
    print("%s - Brew Stats %s" % (get_print_time(), p["name"]))
    log.log_command("Illuminati Store", p["name"], args)
    bot.sendMessage(p["id"], r, parse_mode=telegram.ParseMode.MARKDOWN)

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def illumi_time(bot):
    re = man.illumi_time_check()
    if re is not None:
        bot.sendMessage(id_test, re)

def give_money(bot, update, args):
    p = packet(update, args)
    print("%s - Brew Stats %s" % (get_print_time(), p["name"]))
    log.log_command("Give Money", p["name"], args)
    bot.sendMessage(p["id"], man.give_money(p))

def terasta(bot, update, args):
    p = packet(update, args)
    bot.sendMessage(p["id"], "Terästit kahviasi koskenkorvalla.")

def brew_notify(bot, update, args):
    p = packet(update, args)
    bot.sendMessage(p["id"], man.brew_notify(p))

def brew_cancel(bot, update, args):
    p = packet(update, args)
    bot.sendMessage(p["id"],man.brew_cancel(p))



def main():
    updater = Updater(man.settings["authkey"]) #brew bot
    #updater = Updater("153444739:AAEi7X-cLpDH-n1tT8ZY0McSKg27hKikM5E") #gmf rpg
    dp = updater.dispatcher
    j_que = updater.job_queue
    j_que.put(brew_timer, 1)
    j_que.put(illumi_time, 2)
    print("Brew 0.8 + Items&Drops DLC + ILLUMICOFFEE")

    dp.addTelegramCommandHandler("brew", brew)
    dp.addTelegramCommandHandler("brew_stats", brew_stats)
    dp.addTelegramCommandHandler("brew_score", brew_score)
    dp.addTelegramCommandHandler("brew_check", brew_check)
    dp.addTelegramCommandHandler("brew_inventory", brew_inventory)
    dp.addTelegramCommandHandler("brew_remove", brew_remove)
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

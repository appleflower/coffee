#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, pickle
from random import choice, randint
import datetime, re, humanize
from mods import coffee
from operator import attrgetter
from mods import illumicoffee
from math import sqrt

class manager:
    def __init__(self):
        def load_file(path, json_bool):
            if not json_bool:
                try:
                    with open(path, "rb") as f:
                        return pickle.load(f)
                except:
                    print("Error loading " + path)
                    return {}
            else:
                try:
                    with open(path, "r") as f:
                        return json.load(f)
                except ValueError:
                    print("Error loading settings")
                    return {}

        self.msg_que = []
        self.brewers = load_file("mods/brewers2.p", False)
        self.brew_que = load_file("mods/brew_que.p", False)
        self.illuminati = load_file("mods/illuminati.p", False)
        self.settings = load_file("settings.json", True)

        try:
            top_brews = []
            for x in self.brewers:
                top_brews.append(self.brewers[x].best_coffee)
            self.top_brew = max(top_brews)
        except ValueError:
            self.top_brew = 0

    def human_number(self, number):
        if number < 1000:
            return number
        elif number < 10000:
            number = str(number)
            return number[:1] + " " + number[1:]
        elif number < 100000:
            number = str(number)
            return number[:2] + " " + number[2:]
        elif number < 1000000:
            number = str(number)
            return number[:3] + " " + number[3:]
        else:
            return humanize.intword(number)

    def save_file(self):
        d = {"mods/brew_que.p": self.brew_que,
             "mods/brewers2.p": self.brewers,
             "mods/illuminati.p": self.illuminati}
        for path, obj in d.items():
            with open(path, "wb") as outfile: pickle.dump(obj, outfile)

    def brew_score(self, p):
        top_score = []
        total_coffees = 0

        if len(list(self.brewers.keys())) == 0:
            top_score_txt = "ERROR CD:C//.DEL.FOLDER()"
        elif len(list(self.brewers.keys())) == 1:
            for x in self.brewers:
                top_score.append((self.brewers[x].best_coffee,self.brewers[x].name))
                total_coffees += self.brewers[x].coffees
                top_score.sort(reverse=True)
            top_score_txt = "#1 {0} - *{1}*\n" \
                            "Total coffees brewed: {2}".format(top_score[0][1], self.human_number(top_score[0][0]), total_coffees)
        elif len(list(self.brewers.keys())) == 2:
            for x in self.brewers:
                top_score.append((self.brewers[x].best_coffee,self.brewers[x].name))
                total_coffees += self.brewers[x].coffees
                top_score.sort(reverse=True)
            top_score_txt = "#1 {0} - *{1}*\n" \
                            "#2 {2} - {3}\n" \
                            "Total coffees brewed: {4}".format(top_score[0][1],self.human_number(top_score[0][0]),
                                                               top_score[1][1],self.human_number(top_score[1][0]),
                                                               total_coffees)
        else:
            for x in self.brewers:
                top_score.append((self.brewers[x].best_coffee,self.brewers[x].name))
                total_coffees += self.brewers[x].coffees
                top_score.sort(reverse=True)
            top_score_txt = "#1 {0} - *{1}*\n" \
                            "#2 {2} - {3}\n" \
                            "#3 {4} - {5}\n" \
                            "Total coffees brewed: {6}".format(
                    top_score[0][1],self.human_number(top_score[0][0]),
                    top_score[1][1],self.human_number(top_score[1][0]),
                    top_score[2][1],self.human_number(top_score[2][0]),
                    total_coffees)

        self.msg_que.append((p["id"], "Top Scores:\n{0}".format(top_score_txt)))

    def brew_stats(self, p):
        if len(p["args"]) != 0:
            name = p["args"][0]
        else:
            name = p["name"]
        if name in self.brewers.keys():
            self.msg_que.append((p["id"], self.brewers[name].get_stats()))
        else:
            self.msg_que.append((p["id"],  name + " ei ole keittänyt kahvia."))

    def queue_coffee(self, p):
        def get_args(args):
            timer = 1
            max = self.settings["br_max_timer"]
            if len(args) == 1:
                try:
                    args[0] = int(args[0])
                except ValueError:
                    timer = 1
                if type(args[0]) == int:
                    if args[0] > max:
                        timer = max
                    elif args[0] < 0:
                        timer = 1
                    elif args[0] == 0:
                        timer = 1
                    else:
                        timer = args[0]
            else:
                timer = 1
            return timer

        if p["name"] not in self.brewers.keys():
            self.brewers[p["name"]] = coffee.coffee(p["name"])

        if p["name"] not in self.brew_que.keys():
            timer = get_args(p["args"])
            due = datetime.datetime.now() + datetime.timedelta(minutes=timer)
            self.brew_que[p["name"]] = {"due": due,
                                        "timer": timer,
                                        "id": p["id"],
                                        "msg_id": p["msg_id"],
                                        "name": p["name"]}

            self.save_file()

            if timer == 600:
                now = datetime.datetime.now().time()
                time_morning = datetime.time(hour= 4, minute= 0)
                time_evening = datetime.time(hour= 22, minute= 0)

                if now > time_evening or now < time_morning:
                    self.msg_que.append("HYVÄÄ YÖTÄ %s" % p["name"].upper())

            if timer <= 60:
                self.msg_que.append((p["id"], "Kahvisi on valmista %s minuutissa" % timer))
            else:
                done_h, done_m = str(due.hour), str(due.minute)
                if len(done_h) == 1: done_h = "0" + done_h
                if len(done_m) == 1: done_m = "0" + done_m
                txt = "Kahvisi on valmista %s:%s" % (done_h, done_m)
                self.msg_que.append((p["id"], txt))
        else:
            timer = self.brew_que[p["name"]]["due"]
            done_in = timer - datetime.datetime.now()
            if done_in.seconds < 3600:
                self.msg_que.append((p["id"],
                                     "Edellinen kahvisi on valmista %s minuutin päästä" % round(done_in.seconds / 60)))
            else:
                done = datetime.datetime.now() + datetime.timedelta(seconds=done_in.seconds)
                self.msg_que.append((p["id"], "Edellinen kahvisi on valmista %s:%s" % (done.hour, done.minute)))

    def brew(self, name, timer):
        score, txt = self.brewers[name].brew2(timer)
        if score > self.top_brew:
            txt += "\nNew top score!"
            self.top_brew = score
        self.save_file()

        return txt

    def brew_timer(self):
        time = datetime.datetime.now()
        for x in self.brew_que:
            if self.brew_que[x]["due"] < time:
                try:
                    if self.brewers[self.brew_que[x]["name"]].notify_reply:
                        msg_id = self.brew_que[x]["msg_id"]
                    else:
                        msg_id = None
                except:
                    msg_id = None
                r, id = self.brew(x, self.brew_que[x]["timer"]), self.brew_que[x]["id"]
                del self.brew_que[x]
                self.save_file()
                return r, id, msg_id
        return None

    def brew_check(self, p):
        name = p["name"]
        if name not in self.brew_que.keys():
            self.msg_que.append((p["id"], "Et keitä tällä hetkellä kahvia"))
        else:
            timer = self.brew_que[p["name"]]["due"]
            done_in = timer - datetime.datetime.now()
            if done_in.seconds < 3600:
                self.msg_que.append((p["id"],
                                     "Edellinen kahvisi on valmista %s minuutin päästä" % round(done_in.seconds / 60)))
            else:
                done = datetime.datetime.now() + datetime.timedelta(seconds=done_in.seconds)
                done_h, done_m = str(done.hour), str(done.minute)
                if len(done_h) == 1: done_h = "0" + done_h
                if len(done_m) == 1: done_m = "0" + done_m
                self.msg_que.append((p["id"],  "Edellinen kahvisi on valmista %s:%s" % (done_h, done_m)))

    def brew_inventory(self, p):
        arg, id, name = p["args"], p["id"], p["name"]

        if len(arg) == 0:
            self.msg_que.append((id, self.brewers[name].inventory_view()))
        else:
            try:
                slot = int(arg[0]) - 1
            except ValueError:
                self.msg_que.append((id, "Error: not int."))
                return
            if slot > 3:
                self.msg_que.append((id,  "Error: index over 4."))
                return

            if name in self.brewers.keys():
                if len(self.brewers[name].inventory.items) is not 0:
                    try:
                        r = self.brewers[name].item_remove(slot)
                    except IndexError:
                        r = "Error: no item in slot"

                    self.save_file()
                    self.msg_que.append((id,  r))
                else:
                    self.msg_que.append((id,  "Sinulla ei ole itemeitä."))

    def cons_use(self, p):
        arg, name, id = p["args"][0], p["name"], p["id"]

        if arg == "all":
            if name in self.brewers.keys():
                if len(self.brewers[name].inventory.consumables) is not 0:
                    for i in range(0, len(self.brewers[name].inventory.consumables)):
                        r = self.brewers[name].cons_use(0)
                        self.msg_que.append((id, r))
                    self.save_file()
                else:
                    self.msg_que.append((id, "Sinulla ei ole itemeitä."))
        else:
            try:
                slot = int(arg) - 1
            except ValueError:
                self.msg_que.append((id, "Error: not int."))
                return
            if slot > 3:
                self.msg_que.append((id, "Error: index over 4."))
                return

            if name in self.brewers.keys():
                if len(self.brewers[name].inventory.consumables) is not 0:
                    try:
                        r = self.brewers[name].cons_use(slot)
                    except IndexError:
                        r = "Error: no consumable in slot"

                    self.save_file()
                    self.msg_que.append((id, r))
                else:
                    self.msg_que.append((id, "Sinulla ei ole itemeitä."))

    def brew_status(self):
        avgs = []
        for x in self.brewers: avgs.append(self.brewers[x].avg_score)
        txt = "*Average score:* %s\n" % self.human_number(round((sum(avgs) / len(avgs))))

        avgs = []
        for x in self.brewers: avgs.append(self.brewers[x].best_coffee)
        txt += "*Average best score:* %s\n" % self.human_number(round((sum(avgs) / len(avgs))))

        avgs = []
        for x in self.brewers: avgs.append(self.brewers[x].lvl)
        txt += "*Average lvl:* %s\n" % self.human_number(round((sum(avgs) / len(avgs))))

        if len(self.brew_que) > 0:
            txt += "*Tulevat kahvit:*\n"
            for x in self.brew_que:
                if not self.brew_que[x]["random"]:
                    if len(str(self.brew_que[x]["due"].minute)) == 1:
                        minute = "0" + str(self.brew_que[x]["due"].minute)
                    else:
                        minute = self.brew_que[x]["due"].minute
                    txt += "    *{0}:* {1}:{2}\n".format(x, self.brew_que[x]["due"].hour, minute)

        return txt

    def rahka(self):
        avgs = []
        for x in self.brewers: avgs.append(self.brewers[x].avg_score)
        txt = "*Average score:* %s\n" % self.human_number(round((sum(avgs) / len(avgs))))

        avgs = []
        for x in self.brewers: avgs.append(self.brewers[x].best_coffee)
        txt += "*Average best score:* %s\n" % self.human_number(round((sum(avgs) / len(avgs))))

        avgs = []
        for x in self.brewers: avgs.append(self.brewers[x].lvl)
        txt += "*Average lvl:* %s\n" % self.human_number(round((sum(avgs) / len(avgs))))

        sorted_queue = sorted(self.brew_que.values(), key=attrgetter('due'))
        if len(sorted_queue) > 0:
            txt += "*Tulevat kahvit:*\n"
            for x in sorted_queue:
                if len(str(sorted_queue[x]["due"].minute)) == 1:
                    minute = "0" + str(sorted_queue[x]["due"].minute)
                else:
                    minute = sorted_queue[x]["due"].minute
                txt += "    *{0}:* {1}:{2}\n".format(x, sorted_queue[x]["due"].hour, minute)

        return txt

    def make_new_game(self):
        lvls = []
        for name, obj in self.brewers.items():
            lvls.append(obj.lvl)

        avg = sum(lvls) / len(lvls)
        users = []
        for name, obj in self.brewers.items():
            bonus = round(obj.lvl / avg * 10)
            if bonus > 10: bonus = 10
            coffees = obj.coffees
            old_bonus = obj.prestige_bonus
            users.append({"name": name, "coffees": coffees, "prestige_bonus": bonus + old_bonus})

        for x in users:
            self.brewers[x["name"]] = coffee.coffee(x["name"])
            self.brewers[x["name"]].coffees = x["coffees"]
            self.brewers[x["name"]].prestige_bonus = x["prestige_bonus"]

        self.illuminati = illumicoffee.illuminati()
        self.save_file()

    def illumi_update_event_minus(self):
        for name in self.brewers.keys():
            for event in self.illuminati.active_events:
                attrb = event["attrb"]
                potency = event["potency"]
                self.brewers[name].event_minus[attrb] = potency
                self.save_file()

    def illumi_time_check(self):
        re = self.illuminati.time_check(True)
        if re[0]:
            self.illumi_update_event_minus()
            self.save_file()
            txt = "Uusi Illuminatin juoni:\n" \
                   "{0}\n" \
                   "{1} -{2}%".format(re[1]["desc"],
                                      re[1]["attrb"].capitalize(),
                                      re[1]["potency"])
            self.msg_que.append((None, txt))
        re = self.illuminati.time_check(False)
        if re == "nwo":
            self.brewers = {}
            self.brew_que = {}
            self.illuminati = illumicoffee.illuminati()
            self.save_file()
            self.msg_que.append((None,
                                 "Illuminati sai valmiiksi New World Orderin ja kaikki kahvinkeittimet tuhottiin."))

        elif re == "time machine":
            self.make_new_game()
            self.msg_que.append((None, "Saitte aikakoneen valmiiksi "
                                       "ja pakenitte menneisyyteen estämään Illuminatin hirmuvaltaa."))
        else:
            self.save_file()
            self.msg_que.append((None, None))

    def illumi_stats(self, p):
        def format_time(time):
            def b_n(num):
                if len(str(num)) is 1:
                    return "0" + str(num)
                else:
                    return num
            txt = "{0}.{1} - {2}:{3}".format(
                b_n(time.day), b_n(time.month), b_n(time.hour), b_n(time.minute)
            )

            return txt

        if len(p["args"]) == 0:
            txt = "[Illuminati raportti:](www.gmf.fi/blank):\n" \
                  "*NWO alkaa*\n {0}\n" \
                  "*Aikakone valmistuu*\n {1}\n".format(
                format_time(self.illuminati.game_end),
                format_time(self.illuminati.time_machine_complete))

            if len(self.illuminati.active_events) > 0:
                txt += "[Illuminatin juonet:](www.gmf.fi/blank)\n"
                for x in self.illuminati.active_events:
                    txt += "{0}: -{1}%\n".format(x["attrb"].capitalize(),
                                               x["potency"])
                txt += "Juonen voi tuhota lähettämällä 1000 shekeliä /illuminati x (x = slot)."

            self.msg_que.append((p["id"], txt))
        else:
            try:
                if self.brewers[p["name"]].money < 1000:
                    print("money")
                    self.msg_que.append((p["id"], "Sinulla ei ole tarpeeksi rahaa juonen tuhoamiseen."))
                else:
                    slot = int(p["args"][0]) - 1
                    self.illuminati.active_events.pop(slot)
                    self.illumi_update_event_minus()
                    self.brewers[p["name"]].money -= 1000
                    self.save_file()
                    self.msg_que.append((p["id"], "Ilkeä juoni tuhottu."))
            except:
                self.msg_que.append((p["id"], "Slot error"))

    def illumi_shop(self, p):
        name, args, id = p["name"], p["args"], p["id"]
        if len(args) is 0:
            self.msg_que.append((p["id"],  self.illuminati.shop_view()))
        else:
            if args[0] == "reset":
                if self.brewers[name].money < 500:
                    self.msg_que.append((id, "Sinulla ei ole tarpeeksi rahaa"))
                else:
                    self.brewers[name].money -= 500
                    self.illuminati.shop = self.illuminati.shop_new()
                    self.msg_que.append((id, "Resetoit kaupan!!"))
            else:
                try:
                    slot = int(args[0]) - 1
                    new_item = self.illuminati.shop_buy(slot, self.brewers[name].money)
                    if not new_item[0]:
                        self.msg_que.append((p["id"], new_item[1]))
                    else:
                        new_item = new_item[1]
                        if new_item[0] == "item":
                            if len(self.brewers[name].inventory.items) == 4:
                                self.brewers[name].inventory.items.pop(3)
                            self.brewers[name].inventory.items.append(new_item[2])
                            self.brewers[name].money -= new_item[1]
                            self.brewers[name].item_affix_add()
                            self.save_file()
                            self.msg_que.append((p["id"], "Esine ostettu."))
                        elif new_item[0] == "cons":
                            if len(self.brewers[name].inventory.consumables) == 4:
                                self.brewers[name].inventory.consumables.pop(3)
                            self.brewers[name].inventory.consumables.append(new_item[2])
                            self.brewers[name].money -= new_item[1]
                            self.save_file()
                            self.msg_que.append((p["id"], "Esine ostettu."))
                        elif new_item[0] == "aikakone":
                            self.brewers[name].money -= new_item[1]
                            self.save_file()
                            self.msg_que.append((p["id"], "Nopeutit aikakoneen valmistumista %s tunnilla." % new_item[2]))

                except:
                    self.msg_que.append((p["id"], "Invaliidi slotti."))

    def give_money(self, p):
        name, to = p["name"], p["args"][0]
        try:
            amount = int(p["args"][1])
        except:
            self.msg_que.append((p["id"], "Invaliidi value"))
            return

        if amount > self.brewers[name].money:
            self.msg_que.append((p["id"], "Sinulla ei ole tarpeeksi rahaa."))
        else:
            self.brewers[name].money -= amount
            self.brewers[to].money += amount
            self.save_file()
            self.msg_que.append((p["id"], "%s siirretty %s tilille." % (amount, to)))

    def brew_notify(self, p):
        name = p["name"]
        if self.brewers[name].notify_reply:
            self.brewers[name].notify_reply = False
            self.msg_que.append((p["id"], "Kahvisi ei enää piippaa."))
        else:
            self.brewers[name].notify_reply = True
            self.msg_que.append((p["id"], "Kahvisi piippaa kun se on valmista."))

    def brew_cancel(self, p):
        name = p["name"]
        for b_name in self.brew_que.keys():
            if name == b_name:
                del self.brew_que[b_name]
                self.msg_que.append((p["id"], "Kaadoit kahvisi viemäriin"))
        self.msg_que.append((p["id"], "Et keitä tällä hetkellä kahvia."))

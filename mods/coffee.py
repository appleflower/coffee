from random import uniform, choice,randint
import xml.etree.ElementTree as etree
from datetime import datetime
from datetime import timedelta
from math import ceil
import humanize
from mods.item2 import inventory
from mods import logger_sys as log
from mods.farm import farm
import json

class coffee():
    def __init__(self, name):
        self.name = name
        self.lvl = 1
        self.coffees = 0
        self.exp = 0
        self.best_coffee = 0
        self.avg_score = 30
        self.drop_chance = 10
        self.last_brew = None
        self.inventory = inventory()
        self.event_minus = {"score": 0, "exp": 0, "grade": 0, "drop": 0}
        self.prestige_bonus = 0
        self.money = 0
        self.notify_reply = False

    def update_things(self):
        self.inventory = inventory()

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

    def get_stats(self):
        req_exp = 20 + self.lvl * 2 + (self.lvl ** 3)
        exp = "%s/%s" % (self.human_number(self.exp), self.human_number(ceil(req_exp)))

        txt = "[{0}:](www.gmf.fi/blank)\n" \
              "*Lvl:* {1} ({2})\n" \
              "*Top Brew:* {3}, *Total Brews:* {4}\n" \
              "*Money:* {5}, *Scraps:* {7} *Prestige bonus:* {6}%\n".format(
                self.name,
                self.human_number(self.lvl),
                exp,
                self.human_number(self.best_coffee),
                self.coffees,
                self.money,
                self.prestige_bonus,
                self.inventory.scraps)

        txt += "\n[Bonuses:](www.gmf.fi/blank)\n"
        for x in self.inventory.item_bonus:
            if self.inventory.item_bonus[x] is not 0:
                txt += "*{0}*: {1}%\n".format(x.capitalize(), self.inventory.item_bonus[x])
        return txt

    def brew2(self, time):
        def anti_cheat(set, value):
            def load():
                try:
                    with open("mods/cheater.json", "r") as f:
                        return json.load(f)
                except ValueError:
                    print("Error loading settings")
                    return {}

            def save(file):
                with open('mods/cheater.json', 'w') as outfile:
                    json.dump(file, outfile)

            r = load()
            name, times, miinus = r["name"], r["times"], r["minus"]

            if set:
                if name == "Dragory":
                    if time > 8 and time < 15:
                        times += 1
                        if times >= 3:
                            miinus += 20
                    else:
                        times = 0
                        miinus = 0
                    r["times"], r["minus"] = times, miinus
                    save(r)
            else:
                if name == "Dragory":
                    ov = value
                    value *= (100 - miinus) / 100
                    value = round(value)
                    if value < 0:
                        value = 1
                    print("old: %s, new: %s" % (ov, value))
                    return value

        cons_bonus = self.inventory.cons_bonus
        item_bonus = self.inventory.item_bonus
        #anti_cheat(True, 0)

        def get_minus_score(score):
            return_score = score
            minus = 0
            cur_time = datetime.now()
            if self.last_brew != None:
                if cur_time < self.last_brew + timedelta(minutes=10):
                    minus = 90
                elif cur_time < self.last_brew + timedelta(minutes=30):
                    minus = 50
                elif cur_time < self.last_brew + timedelta(minutes=60):
                    minus = 10
                else:
                    minus = 0
            else:
                minus = 0

            if minus != 0:
                return_score *= 1 - (minus / 100)

            self.last_brew = datetime.now()

            return return_score, minus

        def get_grade(score, timer, minus, coffee_crit):

            def get_text(grade):
                grade += 1
                grade_text_dic = {1:"Pleb Coffee",2:"Regular Coffee",3:"Good Coffee",4:"Master Coffee",5:"Gods Coffee"}
                lvl_up, gained_lvls, exp_gained = self.check_lvl(grade, score)

                g_text = grade_text_dic[grade]

                try:
                    e_root = etree.parse("mods/text.xml").getroot()
                except FileNotFoundError:
                    e_root = etree.parse("text.xml").getroot()
                #pr = choice(e_root[0].findall("l")).text
                aksu = choice(e_root[0].findall("a")).text
                #adj = choice(e_root[grade].findall("adj")).text
                #teko = choice(e_root[grade].findall("teko")).text

                if minus == 0:
                    minus_score = 100
                else:
                    minus_score = 100 - minus

                #item code money
                if minus_score > 40:
                    money = randint(30, 50) * grade
                    money *= ceil(item_bonus["drop"] + cons_bonus["drop"]) / 100 + 1
                    money *= self.prestige_bonus / 100 + 1
                    money *= 1 - (self.event_minus["drop"] / 100)
                    money = ceil(money)
                    #money = anti_cheat(False, money)
                    self.money += money
                else:
                    money = randint(1, 10)
                    money *= ceil(item_bonus["drop"] + cons_bonus["drop"]) / 100 + 1
                    money *= self.prestige_bonus / 100 + 1
                    money *= 1 - (self.event_minus["drop"] / 100)
                    money = ceil(money)
                    #anti_cheat(False, money)
                    self.money += money

                if self.notify_reply:
                    txt = "Kahvisi:\n"
                    if self.name == "spittis":
                        txt = "*spitti*-sensein kahvi:\n"
                    elif self.name == "Dragory":
                        txt = "*Dragory*-saman kahvi:\n"
                else:
                    txt = "*%s*, kahvisi:\n" % self.name

                txt += "Score: *{0}*, Grade: *{1}*, Quality: *{2}*%{4}\n" \
                       "Aksun mielipide: {3}".format(
                        self.human_number(int(score)),
                        g_text,
                        minus_score,
                        aksu,
                        ("" if self.notify_reply is True else ", Time: *%s*." % timer))

                if money > 0:
                    txt += "\n`[MONEY]` *+%s shekels*" % money

                if exp_gained:
                    txt += "\n`[EXP]` *+%s exp*" % exp_gained

                if lvl_up:
                    txt += "\n`[LVLUP]` *+{0} {1}*".format(gained_lvls, ("lvl" if gained_lvls == 1 else "lvls"))

                if coffee_crit:
                    txt += "\n`[CRIT]` *DING DING*"

                #item code drop
                if minus_score > 50:
                    bonus_drop_c = ceil(item_bonus["drop"] + cons_bonus["drop"]) / 100 + 1
                    bonus_drop_c *= 1 - (self.event_minus["drop"] / 100)
                    self.drop_chance *= bonus_drop_c
                    if randint(0, 100) < self.drop_chance:
                        txt += "\n`[DROP]` %s" % self.inventory.item_drop()
                        self.drop_chance = 10
                    else:
                        self.drop_chance += 10

                    if len(self.inventory.consumables) < 4:
                        if randint(0, 50) < self.drop_chance:
                            txt += "\n`[DROP]` %s" % self.inventory.cons_drop()

                    return txt
                else:
                    return txt

            if score / self.avg_score < 1: grade = 0
            elif score / self.avg_score < 1.5: grade = 1
            elif score / self.avg_score < 2: grade = 2
            elif score / self.avg_score < 3: grade = 3
            else: grade = 4

            if score > self.avg_score:
                self.avg_score = (self.avg_score + score) / 2

            #item code
            grade_bonus = ceil(item_bonus["grade"] + cons_bonus["grade"])
            if randint(0, 100) < grade_bonus:
                grade += 1
            if grade > 4: grade = 4

            return get_text(grade)

        def soul():
            def get_time_number():
                time1,time2,time3 = str(datetime.now().microsecond)[0:2], \
                                    str(datetime.now().microsecond)[2:4], \
                                    str(datetime.now().microsecond)[4:6]
                time_list = [time1, time2, time3]

                def reduce_number(x):
                    x = str(x)
                    if len(x) == 1: x += "0"
                    elif len(x) == 0: x = "00"

                    n_1, n_2 = int(x[0]), int(x[1])

                    return n_1 + n_2

                for i in range(0,3):
                    x = time_list[i]
                    x = reduce_number(x)
                    if x >= 10:
                        x = reduce_number(str(x))
                    time_list[i] = x

                time_total = reduce_number(sum(time_list))
                if time_total == 10:
                    time_total = 1

                return time_total

            def get_fortune():
                tarot = {"ace": 2, "change": 1, "works": 1, "power": 1, "worry": 0, "success": 2,
                         "failure": 0, "prudence": 1, "gain": 1, "wealth": 2}
                fortune = choice(list(tarot.keys()))
                if tarot[fortune] == 2:
                    return "good"
                elif tarot[fortune] == 1:
                    return "neutral"
                else:
                    return "bad"

            fortune = get_fortune()

            if fortune == "bad":
                min_num = 0.7
            elif fortune == "neutral":
                min_num = 0.9
            else:
                min_num = 1

            max_num = 1 + (get_time_number() / 10)

            return min_num, max_num

        def get_r(x, min, max):
            return round(x * uniform(min, max), 2)

        steps = (10 + self.lvl * 10) / 3
        prep_steps, brew_steps, serv_steps = round(steps), round(steps), round(steps)
        steps = [prep_steps, brew_steps, serv_steps]
        score = 0

        def do_step(step):
            step_score = 0
            while step >= 0:
                step_score += get_r(self.lvl, 1, 2)
                step -= 1
            return round(step_score)

        for x in steps:
            score += do_step(x)

        time_step = time
        while time_step >= 0:
            if time_step < 100:
                score *= 1.02
            if time_step < 300:
                score *= 1.01

            time_step -= 1

        soul_score = soul()
        score = get_r(score, soul_score[0], soul_score[1])

        #item code score
        score *= item_bonus["score"] / 100 + 1
        score *= cons_bonus["score"] / 100 + 1
        score *= self.prestige_bonus / 100 + 1
        score *= 1 - (self.event_minus["score"] / 100)

        coffee_crit = False
        if cons_bonus["crit"] != 0:
            if randint(0, 100) < cons_bonus["crit"]:
                coffee_crit = True
                score *= 1.5

        score, minus = get_minus_score(score)
        score = round(score)

        self.coffees += 1
        if score > self.best_coffee:
            self.best_coffee = score

        self.inventory.cons_bonus = {"score": 0, "exp": 0, "grade": 0, "drop": 0, "crit": 0}

        log.log_brew(self.name, time, score, self.lvl)
        return score, get_grade(score, time, minus, coffee_crit)

    def lvl_up(self):
        self.lvl += 1

    def check_lvl(self, grade, score):
        lvl_exponent = 3

        gained_exp = ceil(score / 100 * grade)
        #item code exp
        gained_exp *= self.inventory.item_bonus["exp"] / 100 + 1
        gained_exp *= self.inventory.cons_bonus["exp"] / 100 + 1
        gained_exp *= self.prestige_bonus / 100 + 1
        gained_exp *= 1 - (self.event_minus["exp"] / 100)
        gained_exp = round(gained_exp)

        lvl_up = False
        lvls_gained = 0

        req_exp = ceil(20 + self.lvl * 2 + (self.lvl ** lvl_exponent))
        self.exp += gained_exp
        while self.exp >= req_exp:
            self.exp -= req_exp
            self.lvl_up()
            lvls_gained += 1
            lvl_up = True
            req_exp = ceil(20 + self.lvl * 2 + (self.lvl ** lvl_exponent))

        self.exp = ceil(self.exp)
        return lvl_up, lvls_gained, gained_exp

    def item_remove(self, slot):
        try:
            i = self.inventory.items[slot]
        except IndexError:
            return "Itemiä ei löytynyt slotista"

        return self.inventory.item_remove(slot)

    def cons_use(self, slot, use_all):
        if use_all:
            if len(self.inventory.consumables) is not 0:
                self.inventory.cons_set_bonus(0, True)
                return self.inventory.cons_bonus_print()
            else:
                return "Sinulla ei ole consumableja."
        else:
            if len(self.inventory.consumables) is not 0:
                try:
                    self.inventory.cons_set_bonus(slot, False)
                    return self.inventory.cons_bonus_print()
                except IndexError:
                    return "Consumablea ei löytynyt slotista."
            else:
                return "Sinulla ei ole consumableja."

    def inventory_view(self):
        return self.inventory.get_inv_txt()

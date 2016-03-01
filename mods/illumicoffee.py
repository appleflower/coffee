import datetime, pickle
import mods.item as item
from random import randint, choice
from mods import logger_sys as log

class arpa():
    def __init__(self):
        self.all_players = []
        self.players = []
        self.prizes = self.prize_pool_create()
        self.cost = 1000
        date = datetime.date.today()
        self.end_time = datetime.datetime(year=date.year, month=date.month, day=date.day, hour=23, minute=59)

    def player_add(self, name):
        if name in self.players:
            return False
        else:
            self.players.append(name)
            return True

    def prize_pool_create(self):
        def get_from_type(whatuwant):
            i = item.item().create_item()
            while i["type"] is not whatuwant:
                i = item.item().create_item()
            return i

        r = [
            get_from_type("Common"),
            get_from_type("Rare"),
            get_from_type("Epic"),
            get_from_type("Celestial")
        ]
        return r

    def allocate_prizes(self):
        def get_text_and_max_prize():
            p_count = len(self.players)
            prize_text = None
            max_prize = None
            if p_count == 0:
                prize_text = "Kukaan ei ostanut arpaa päivän arpajaisiin."
            elif p_count == 1:
                prize_text = "Vain %s uhrautui ostamaan arvan, eikä arpajaisia pidetty loppuun." % self.players[0]
            elif p_count == 2:
                max_prize = "Common"
            elif p_count == 3:
                max_prize = "Rare"
            elif p_count == 4:
                max_prize = "Epic"
            elif p_count > 4:
                max_prize = "Celestial"

            return max_prize, prize_text

        max_prize, prize_text = get_text_and_max_prize()


    def check_time(self):
        if datetime.datetime.now() > self.end_time:
            self.allocate_prizes()

class illuminati():
    def __init__(self):
        self.item = item.item()
        self.game_end = datetime.datetime.now() + datetime.timedelta(days=10)
        self.time_machine_complete = datetime.datetime.now() + datetime.timedelta(days=9, hours=12)
        self.shop = self.shop_new()
        self.events = self.events_creator()
        self.active_events = []

    def prune_inv(self):
        self.item.consumables = []
        self.item.items = []

    def save_file(self,filename,file):
        with open(filename,"wb") as outfile: pickle.dump(file,outfile)

    ##active_events[x][2] = {attrb, desc, potency}
    def events_creator(self):
        now = datetime.datetime.now()
        def event_create(potency, days, hour_max):
            attributes = ["score", "exp", "drop"]
            desc = ["Illuminati nosti kahvin veroa.", "Illuminati lähetti agentteja tuhoamaan laittomia kahvipanimoita",
                    "Illuminati geenimuunnelsi kahvia aiheuttamaan syöpää.", "Juutalaiset pankkiirit nostivat kahvin veroa."]

            event = {"attrb": choice(attributes), "desc": choice(desc), "potency": potency}
            time = now + datetime.timedelta(days=days) + datetime.timedelta(hours=randint(1, hour_max))

            return [False, time, event]
        lst = [event_create(5, 2, 12), event_create(10, 5, 10), event_create(15, 7, 12)]
        return lst

    def time_check(self, event_check):
        now = datetime.datetime.now()

        if event_check:
            for x in self.events:
                if not x[0]:
                    if now > x[1]:
                        self.active_events.append(x[2])
                        x[0] = True
                        log.log_illumi("New Dark event")
                        return True, x[2]
            return False, None
        else:
            if now > self.game_end:
                log.log_illumi("NWO complete")
                return "nwo"
            elif now > self.time_machine_complete:
                log.log_illumi("Time Machine complete")
                return "time machine"
            else:
                return None

    def reduce_time(self, game_end, cost):
        if game_end:
            log.log_illumi("Game end time reduction %s minutes" % cost)
            self.game_end -= datetime.timedelta(minutes=cost)
        else:
            log.log_illumi("Time mahcine time reduction %s hours" % cost)
            self.time_machine_complete -= datetime.timedelta(hours=cost)

    def make_item(self, i_type):
        self.prune_inv()
        if i_type is "item":
            item_grade = {"Trash": 100, "Common": 300, "Rare": 800, "Epic": 1000, "Celestial": 2000}
            i = self.item.create_item()
            while i["type"] is "Trash":
                i = self.item.create_item()
            item_cost = item_grade[i["type"]]
            return "item", item_cost, i

        elif i_type is "cons":
            i = self.item.cons_drop()[1]
            return "cons", i["grade"] * 10, i

        elif i_type is "aikakone":
            aikakone_time = randint(1, 24)
            return "aikakone", aikakone_time * 100, aikakone_time

    def shop_new(self):
        items = []
        for x in range(0, 3):
            items.append(self.make_item("item"))
        for x in range(0, 3):
            items.append(self.make_item("cons"))

        items.append(self.make_item("aikakone"))

        return items

    def shop_view(self):
        txt = "Illuminati shop:\n"

        for i in range(0, len(self.shop)):
            i_type, cost, stats = self.shop[i][0], self.shop[i][1], self.shop[i][2]
            if i_type == "item":
                txt += "#{3}. {0} {1}, Hinta: {2}\n".format(stats["type"], stats["name"], cost, i + 1)
            elif i_type == "cons":
                txt += "#{3}. {0} {1}, Hinta: {2}\n".format(stats["name"], stats["grade"], cost, i + 1)
            elif i_type == "aikakone":
                txt += "#{2}. Aikakoneen osa, Bonus: {0}h, Hinta: {1}\n".format(stats, cost, i + 1)
            else:
                print("shop view error")

        txt += "\nOsta kaupasta laittamalla komennon perään haluttu numero. Jos esineelle ei ole tilaa, poistetaan" \
               " *viimeinen* esine inventoorista."
        return txt

    def shop_buy(self, slot, current_money):
        try:
            i = self.shop[slot]
            if i[1] > current_money:
                return False, "Sinulla ei ole rahaa ostaa kyseistä esinettä."
            else:
                log.log_illumi("Shop Buy")
                self.shop.pop(slot)
                if i[0] == "item":
                    self.reduce_time(True, i[1])
                    self.shop.append(self.make_item("item"))
                elif i[0] == "cons":
                    self.reduce_time(True, i[1])
                    self.shop.append(self.make_item("cons"))
                elif i[0] == "aikakone":
                    self.reduce_time(False, i[2])
                    self.shop.append(self.make_item("aikakone"))
                return True, i
        except:
            return False, "Error getting item"

#d = illuminati()
#d.item = item.item()
#d.save_file("illuminati.p",d)
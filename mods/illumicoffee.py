import datetime, pickle
from random import randint, choice
from mods import logger_sys as log
from mods.item2 import item, consumable

class supply_drop():
    def __init__(self):
        self.box = self.drop_create()
        self.dropped = False

    def drop_give(self):
        if len(self.box) is not 0:
            r_index = randint(0, len(self.box))
            r = self.box[r_index]
            self.box.pop(r_index)
            return r
        else:
            return None


    def drop_create(self):
        def get_from_type(whatuwant):
            i = item.item().create_item()
            while i["type"] is not whatuwant:
                i = item.item().create_item()
            return i

        def drop_cons(grade):
            c = item.item().cons_drop()
            c = c[1]
            while c["grade"] is not grade:
                c = item.item().cons_drop()
                c = c[1]
            return c

        box = []
        if randint(0, 9) == 0:
            box.append(get_from_type("Celestial"))
        else:
            box.append(get_from_type("Epic"))

        if randint(0, 1) == 0:
            box.append(get_from_type("Epic"))
        else:
            box.append(get_from_type("Rare"))

        box.append(drop_cons(10))
        box.append(drop_cons(10))
        box.append(drop_cons(10))

        return box

class illuminati():
    def __init__(self):
        self.game_end = datetime.datetime.now() + datetime.timedelta(days=10)
        self.time_machine_complete = datetime.datetime.now() + datetime.timedelta(days=9, hours=12)
        self.shop = self.shop_new()
        self.events = self.events_creator()
        self.active_events = []

    def save_file(self,filename,file):
        with open(filename,"wb") as outfile: pickle.dump(file,outfile)

    def events_creator(self):
        now = datetime.datetime.now()
        def event_create(potency, days, hour_max):
            attributes = ["score", "exp", "drop"]
            desc = ["Illuminati nosti kahvin veroa.", "Illuminati lähetti agentteja tuhoamaan laittomia kahvipanimoita",
                    "Illuminati geenimuunnelsi kahvia aiheuttamaan syöpää.", "Juutalaiset pankkiirit nostivat kahvin veroa."]

            event = {"attrb": choice(attributes), "desc": choice(desc), "potency": potency}
            time = now + datetime.timedelta(days=days) + datetime.timedelta(hours=randint(1, hour_max))

            return [False, time, event]
        lst = [event_create(20, 2, 12), event_create(40, 5, 10), event_create(60, 7, 12)]
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

    # returnaa tuplen #1 type #2 cost #3 object
    def make_item(self, i_type):
        if i_type is "item":
            item_grade = {"Trash": 100, "Common": 300, "Rare": 800, "Epic": 1000, "Celestial": 2000}
            i = item()
            while i.type == "Trash" or i.type == "Common":
                i = item()
            item_cost = item_grade[i.type]
            return "item", item_cost, i

        elif i_type is "cons":
            c = consumable()
            while c.grade < 5:
                c = consumable()
            return "cons", c.grade * 15, c

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
            i_type, cost, obj = self.shop[i][0], self.shop[i][1], self.shop[i][2]
            if i_type == "item":
                assert isinstance(obj, item)
                txt += "#{3}. {0} {1}, Hinta: {2}\n".format(obj.type, obj.name, cost, i + 1)
            elif i_type == "cons":
                assert isinstance(obj, consumable)
                txt += "#{3}. {0} {1}, Hinta: {2}\n".format(obj.name, obj.grade, cost, i + 1)
            elif i_type == "aikakone":
                txt += "#{2}. Aikakoneen osa, Bonus: {0}h, Hinta: {1}\n".format(obj, cost, i + 1)
            else:
                print("shop view error")

        txt += "\nOsta kaupasta laittamalla komennon perään haluttu numero. Jos esineelle ei ole tilaa, poistetaan" \
               " *viimeinen* esine inventoorista.\n" \
               "Päivitä kauppa laittamalla komennon perään reset, hinta 500 shekeliä."
        return txt

    def shop_buy(self, slot, current_money):
        try:
            i = self.shop[slot]
            if i[1] > current_money:
                return False, "Sinulla ei ole rahaa ostaa kyseistä esinettä."
            else:
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

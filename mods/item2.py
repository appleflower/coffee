import xml.etree.ElementTree as etree
from random import choice, randint, uniform
from math import ceil


class item:
    def __init__(self):
        i = self.create()
        self.name = i["name"]
        self.prefix = i["prefix"]
        self.stats = i["affix"]
        self.type = i["type"]
        del i

    def create(self):

        def get_random_by_prob(items):
            total = sum(int(item.get("prob")) for item in items)
            rand = randint(1, total)

            for item in items:
                prob = int(item.get("prob"));
                if rand <= prob:
                    return item

                rand -= prob

            return None

        try:
            item_attrs = etree.parse("mods/text.xml").getroot()
        except FileNotFoundError:
            item_attrs = etree.parse("text.xml").getroot()

        grades = item_attrs.find("grades")
        prefixes = item_attrs.find("prefixes")
        item_names = [x.text for x in item_attrs.find("item_names").findall("name")]

        grade = get_random_by_prob(grades)
        prefix = get_random_by_prob(prefixes)
        name = choice(item_names)

        full_name = prefix.get("name") + " " + name

        # Set the item's stats according to the prefix
        # The higher the grade, the more of the prefix's stats get applied
        stats = {"exp": 0, "score": 0, "grade": 0, "drop": 0}
        available_stats = [x.text for x in prefix.findall("stat")]
        max_stat_count = min(int(grade.get("stat_count")), len(available_stats))

        for x in range(0, max_stat_count):
            stat = available_stats[x]
            stats[available_stats[x]] += 5 * int(grade.get("stat_mult"))

        return {"name": full_name, "prefix": prefix.get("name"), "affix": stats, "type": grade.get("name")}


class consumable:
    def __init__(self):
        c = self.create()
        self.type = c["type"]
        self.grade = c["grade"]
        self.name = c["name"]
        del c

    def get_cons_bonus(self):
        if self.type == "exp":
            return self.grade * 2
        elif self.type == "score":
            return self.grade * 3
        elif self.type == "grade":
            return ceil(self.grade / 2)
        elif self.type == "drop":
            return self.grade * 10
        elif self.type == "crit":
            return self.grade * 2

    def create(self):
        cons_names = {"score": "Pyhä Vesi",
                      "exp": "Ihmekuppi",
                      "grade": "Kahvikirja",
                      "drop": "Kahvikauppias",
                      "crit": "Turbokuppi"}
        drop_type = ["exp", "score", "grade", "drop", "crit"]
        dropped = choice(drop_type)

        res = {"type": dropped, "grade": randint(1, 10), "name": cons_names[dropped]}
        return res


class inventory:
    def __init__(self):
        self.items = []
        self.consumables = []
        self.item_que = None
        self.item_bonus = {"exp": 0, "score": 0, "grade": 0, "drop": 0}
        self.cons_bonus = {"exp": 0, "score": 0, "grade": 0, "drop": 0, "crit": 0}
        self.scraps = 0

    def get_inv_txt(self):
        def get_bonuses(affix):
            re_txt = ""
            affixes = {}
            for x in affix:
                if affix[x] is not 0:
                    affixes[x] = affix[x]
            re_txt = ", ".join(['%s: %s' % (key.capitalize(), value) for (key, value) in affixes.items()])
            return re_txt
        def get_cons_bonuses():
            cons_names = {"score": "Pyhä Vesi",
                          "exp": "Ihmekuppi",
                          "grade": "Kahvikirja",
                          "drop": "Kahvikauppias",
                          "crit": "Turbokuppi"}
            re_txt = ""
            for x in self.consumables:
                re_txt += "{0}, Grade: {1}\n".format(cons_names[x.type], x.grade)

            return re_txt

        if len(self.items) is 0 and len(self.consumables) is 0:
            return "Inventoorisi on tyhjä."
        else:
            items_txt = ""
            if len(self.items) is not 0:
                items_txt = "[Items:](www.gmf.fi/blank)\n"
                for x in self.items:
                    items_txt += "*{0}* - {1}:\n".format(x.type, x.name)
                    items_txt += "{0}\n".format(get_bonuses(x.stats))

            if len(self.consumables) is not 0:
                items_txt += "\n[Consumables:](www.gmf.fi/blank)\n%s" % get_cons_bonuses()

            return items_txt

    def item_set_bonus(self):
        for i in self.items:
            assert isinstance(i, item)
            for stat, value in i.stats.items():
                self.item_bonus[stat] += value

    def cons_set_bonus(self, slot, use_all_cons):
        if use_all_cons:
            for c in self.consumables:
                assert isinstance(c, consumable)
                self.cons_bonus[c.type] += c.get_cons_bonus()
        else:
            tyyppi, value = self.consumables[slot].type, self.consumables[slot].get_cons_bonus()
            self.cons_bonus[tyyppi] += value

    def item_scrap(self, slot):
        scrap_prizes = {"Trash": 100, "Common": 200, "Rare": 300, "Epic": 400, "Celestial": 500}
        i = self.items[slot]
        assert isinstance(i, item)

        total_scraps = scrap_prizes[i.type] * uniform(0.8, 1.2)
        total_scraps *= self.item_bonus["drop"] / 100 + 1

        self.scraps += ceil(total_scraps)
        self.items.pop(slot)

    def item_drop(self):
        if len(self.items) == 4:
            self.item_que = item()
        else:
            self.items.append(item())
            self.item_set_bonus()

    def item_remove(self, slot, add_from_queue):
        if add_from_queue:
            self.item_scrap(slot)
            self.items.append(self.item_que)
            self.item_que = None
        else:
            self.item_scrap(slot)

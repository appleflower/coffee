from random import randint, choice
from math import ceil
import xml.etree.ElementTree as etree

class item:
    def __init__(self):
        self.items = []
        self.consumables = []
        self.item_que = None

        try:
            self.item_attrs = etree.parse("mods/text.xml").getroot()
        except FileNotFoundError:
            self.item_attrs = etree.parse("text.xml").getroot()

        self.grades = self.item_attrs.find("grades")
        self.prefixes = self.item_attrs.find("prefixes")
        self.item_names = [x.text for x in self.item_attrs.find("item_names").findall("name")]

    def item_drop(self):
        res = self.create_item()
        if len(self.items) < 4:
            self.items.append(res)
            return True, res
        else:
            self.item_que = res
            return False, res

    def item_remove(self, slot):
        self.items.pop(slot)

    def cons_drop(self):
        cons_names = {"score": "Pyhä Vesi",
                      "exp": "Ihmekuppi",
                      "grade": "Kahvikirja",
                      "drop": "Kahvikauppias",
                      "crit": "Turbokuppi"}
        drop_type = ["exp", "score", "grade", "drop", "crit"]
        dropped = choice(drop_type)

        if len(self.consumables) < 4:
            res = {"type": dropped, "grade": randint(1, 10), "name": cons_names[dropped]}
            self.consumables.append(res)
            return True, res
        else:
            return False, None

    def get_cons_bonus(self, c_type, grade):
        if c_type == "exp":
            return grade * 2
        elif c_type == "score":
            return grade * 3
        elif c_type == "grade":
            return ceil(grade / 2)
        elif c_type == "drop":
            return grade * 10
        elif c_type == "crit":
            return grade * 2

    def get_random_by_prob(self, items):
        total = sum(int(item.get("prob")) for item in items)
        rand = randint(1, total)

        for item in items:
            prob = int(item.get("prob"));
            if rand <= prob:
                return item

            rand -= prob

        return None

    def create_item(self):
        # Randomize grade, prefix and name
        # Grade and prefix use weighted randoming according to their "prob" attribute
        grade = self.get_random_by_prob(self.grades)
        prefix = self.get_random_by_prob(self.prefixes)
        name = choice(self.item_names)

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
                re_txt += "{0}, Grade: {1}\n".format(cons_names[x["type"]], x["grade"])

            return re_txt

        if len(self.items) is 0 and len(self.consumables) is 0:
            return "Inventoorisi on tyhjä."
        else:
            items_txt = ""
            if len(self.items) is not 0:
                items_txt = "[Items:](www.gmf.fi/blank)\n"
                for x in self.items:
                    items_txt += "*{0}* - {1}:\n".format(x["type"], x["name"])
                    items_txt += "{0}\n".format(get_bonuses(x["affix"]))

            if len(self.consumables) is not 0:
                items_txt += "\n[Consumables:](www.gmf.fi/blank)\n%s" % get_cons_bonuses()

            return items_txt


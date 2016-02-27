from random import randint, choice
from math import ceil
import xml.etree.ElementTree as etree

class item:
    def __init__(self):
        self.items = []
        self.consumables = []
        self.item_que = None

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
        cons_names = {"score": "Pyhä Vesi", "exp": "Ihmekuppi", "grade": "Kahvikirja", "drop": "Kahvikauppias"}
        drop_type = ["exp", "score", "grade", "drop"]
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

    def create_item(self):
        grade_prob = {0: 100, 1: 50, 2: 20, 3: 10, 4: 5}
        grade_text = {0: "Trash", 1: "Common", 2: "Rare", 3: "Epic", 4: "Celestial"}
        grade = None
        while grade is None:
            for x in grade_prob:
                chance = randint(0, sum(grade_prob.values()))
                if grade_prob[x] > chance:
                    grade = x

        try:
            e_root = etree.parse("mods/text.xml").getroot()
        except FileNotFoundError:
            e_root = etree.parse("text.xml").getroot()
        n_1 = choice(e_root[6].findall("pre")).text
        n_2 = choice(e_root[6].findall("end")).text
        item_name = n_1 + " " + n_2

        affix = {"exp": 0, "score": 0, "grade": 0, "drop": 0}
        for x in range(grade + 1):
            stat = ["exp", "score", "grade", "drop"]
            affix[choice(stat)] += randint(1, 5) * (grade + 1)

        return {"name": item_name, "affix": affix, "type": grade_text[grade]}

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
            cons_names = {"score": "Pyhä Vesi", "exp": "Ihmekuppi", "grade": "Kahvikirja", "drop": "Kahvikauppias"}
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


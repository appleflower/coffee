import pickle
from mods import illumicoffee
from mods import coffee
from mods.farm import farm
from importlib import reload

def save_file(filename,file):
    with open(filename, "wb") as outfile: pickle.dump(file, outfile)
#d = illumicoffee.illuminati
#save_file("mods/illuminati.p", d)
#save_file("mods/brew_que.p", d)


with open("mods/brewers2.p","rb") as f:
    try:
        d = pickle.load(f)
    except FileNotFoundError:
        print("Error loading brew_que.p")
        d = {}

for name, obj in d.items():
    print(obj.farm)


save_file("mods/brewers2.p", d)


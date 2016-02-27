import datetime, pickle

def now():
    return datetime.datetime.now()

def save(line):
    pass
    """
    try:
        with open("mods/datafiles/log.p", "rb") as f:
            log = pickle.load(f)
    except:
        with open("datafiles/log.p", "rb") as f:
            log = pickle.load(f)

    log.append(line)

    for i in range(0,len(log)):
        if log[i]["name"] == "kalle":
            log.pop(i)



    try:
        with open("mods/datafiles/log.p", "wb") as outfile: pickle.dump(log, outfile)
    except:
        with open("datafiles/log.p", "wb") as outfile: pickle.dump(log, outfile)
    """

def make_txt_file():

    def format_time(time):
            def b_n(num):
                if len(str(num)) is 1:
                    return "0" + str(num)
                else:
                    return num
            txt = "{0}.{1} {2}:{3}".format(
                b_n(time.day), b_n(time.month), b_n(time.hour), b_n(time.minute)
            )

            return txt

    try:
        with open("mods/datafiles/log.p", "rb") as f:
            log = pickle.load(f)
    except:
        with open("datafiles/log.p", "rb") as f:
            log = pickle.load(f)

    txt = ""
    for line in log:
        if line["type"] == "general":
            txt += "{0} {1} - {2}\n".format(
                format_time(line["time"]),
                line["type"].capitalize(),
                line["event"]
            )
        elif line["type"] == "brew":
            txt += "{0} {1} - {2}, Score: {3}, Timer: {4}, Lvl: {5}\n".format(
                format_time(line["time"]),
                line["type"].capitalize(),
                line["name"],
                line["score"],
                line["timer"],
                line["lvl"]
            )
        elif line["type"] == "illuminati":
            txt += "{0} {1} - {2}\n".format(
                format_time(line["time"]),
                line["type"].capitalize(),
                line["event"]
            )
        elif line["type"] == "command":
            txt += "{0} {1} - {2}, Command: {3}, Args: {4}\n".format(
                format_time(line["time"]),
                line["type"].capitalize(),
                line["name"],
                line["command"],
                line["args"]
            )
        else:
            pass

    print(txt)

def log_brew(name, timer, score, lvl):
    log = {"type": "brew",
           "name": name,
           "time": now(),
           "score": score,
           "timer": timer,
           "lvl": lvl}
    save(log)

def log_illumi(event):
    log = {"type": "illuminati",
           "event": event,
           "time": now()}
    save(log)

def log_command(command, name, args):
    log = {"type": "command",
           "command": command,
           "name": name,
           "time": now(),
           "args": args}
    save(log)

def log_general(event):
    log = {"type": "general",
           "event": event,
           "time": now()}
    save(log)



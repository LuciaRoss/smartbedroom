import json
from config import hpost,hget,hput,hdel,colorToHue

class Scene():

    @staticmethod
    def get_all_scenes():
        return hget("scenes")

    @staticmethod
    def get_names():
        scenes = Scene.get_all_scenes()
        return [scenes[s]["name"].strip().lower() for s in scenes.keys()]

    @staticmethod
    def find_by_name(name):
        scenes = Scene.get_all_scenes()
        for k in scenes.keys():
            if scenes[k]["name"].lower() == name.lower():
                return k
        return None

    def __init__(self, bid):
        #if scene id passed
        if bid in Scene.get_all_scenes().keys():
            self.bid = bid
        #init from name
        elif Scene.find_by_name(bid):
            self.bid = Scene.find_by_name(bid)
        else:
            raise Exception("No scene named '{0}'".format(bid))

        description = hget("scenes/{0}".format(self.bid))
        self.name = description["name"]
        self.lights = description["lights"]
        self.storelightstate = False
        self.lightstates = description["lightstates"]
        print(self.lightstates)

    @staticmethod
    def create(extra):
        output = hpost("scenes", {"name": extra, "recycle": True, "lights":["5", "6", "7", "8", "9", "10"]})
        print(output)

    def asdict(self):
        asdict = {}
        asdict["name"] = self.name
        #if True, the lightstatesis overwritten by the current light states
        if self.storelightstate:
            asdict["storelightstate"] = self.storelightstate
        return asdict

    def parseString(self, vect):
        #TODO if name more than one word
        for i in range(len(vect)):
            if vect[i] == "name":
                #TODO blacklist of names
                self.name = vect[i+1]
            elif vect[i] == "save":
                self.storelightstate = True
            elif vect[i] == "brighter":
                self.brighter()
                return
            elif vect[i] == "dimmer":
                self.dimmer()
                return
        output = hput("scenes/{0}".format(self.bid), self.asdict())
        print(output)

    def store(self):
        output = hput("scenes/{0}".format(self.bid), {"storelightstate": True})
        print(output)

    def delete(self):
        output = hdel("scenes/{0}".format(self.bid))
        print(output)

    def brighter(self):
        for l in self.lightstates:
            if self.lightstates[l]["on"]:
                bri = int(self.lightstates[l]["bri"])
                bri = min(254, bri + 45)
                output = self.modifyScene(l, {"on": True, "bri": bri})

    def dimmer(self):
        for l in self.lightstates:
            print(l)
            if self.lightstates[l]["on"]:
                bri = int(self.lightstates[l]["bri"])
                bri = max(0, bri - 45)
                output = self.modifyScene(l, {"on": True, "bri": bri})

    def modifyScene(self, lid, state):
        url = "scenes/{0}/lightstates/{1}".format(self.bid, lid)
        return hput(url, state)

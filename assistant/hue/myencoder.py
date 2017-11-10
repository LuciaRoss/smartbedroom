from json import JSONEncoder
import hue


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, hue.scene.Scene):
            return o.asdict()
        elif isinstance(o, hue.bulb.Bulb):
            print("error")
            print(o.name)
            print(o.__dict__)
            return o.__dict__

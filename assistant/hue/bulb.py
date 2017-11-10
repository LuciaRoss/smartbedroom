import json
from config import hpost,hget,hput,hdel,colorToHue

class Bulb:

  @staticmethod
  def get_all_lights():
    return hget("lights")

  @staticmethod
  def find_by_name(name):
    lights = Bulb.get_all_lights()
    for k in lights.keys():
      if lights[k]["name"] == name:
        return k
    return None

  def __init__(self, bid):
    #if bulb id passed
    if bid in Bulb.get_all_lights().keys():
      self.bid = bid
    #init from name
    elif Bulb.find_by_name(bid):
      self.bid = Bulb.find_by_name(bid)
    else:
        raise Exception("No bulb named '{0}'".format(bid))

  def _set_states(self,states):
    hput('lights/{0}/state'.format(self.bid),states)

  def _get_status(self):
    return hget("lights/{0}".format(self.bid))

  def on(self):
    self._set_states({"on":True})

  def off(self):
    self._set_states({"on":False})

  def color(self,colorstring):
    self._set_states({"hue":colorToHue(colorstring)})

    #wrong, read and then modify the current "bri" attribute
  def brighter(self, inc = 25):
    self._set_states({"bri_inc":inc})

  def dim(self,inc = 25):
    self.brighter(-inc)

  def ison(self):
    return self._get_status()["state"]["on"]

  def maxima(self):
      return self._set_states({"on":True,"bri":254,'xy': [0.3691, 0.3719]})

  def nightlight(self):
      return self._set_states({"on":True,"bri":1,'xy': [0.5612, 0.4042]})


import json
from scene import Scene
from config import hpost,hget,hput,hdel,colorToHue

class Group:

  @staticmethod
  def get_all_groups():
    return hget("groups")

  @staticmethod
  def find_by_name(name):
    groups = Group.get_all_groups()
    for k in groups.keys():
      if groups[k]["name"].lower().strip() == name.lower().strip():
        return k
    return None

  def __init__(self, bid):
    #if group id passed
    if bid in Group.get_all_groups().keys():
      self.bid = bid
    #init from name
    elif Group.find_by_name(bid):
      self.bid = Group.find_by_name(bid)
    else:
        raise Exception("No group named '{0}'".format(bid))

  def _set_states(self,states):
    hput('groups/{0}/action'.format(self.bid),states)

  def _get_status(self):
    return hget("groups/{0}".format(self.bid))

  def set_scene(self,scene):
      self._set_states({"scene":Scene.find_by_name(scene)})

  def on(self):
    self._set_states({"on":True})

  def off(self):
    self._set_states({"on":False})

  def color(self,colorstring):
    self._set_states({"hue":colorToHue(colorstring)})

  def brighter(self, inc = 25):
    self._set_states({"bri_inc":inc})

  def warmer(self, inc = 20):
    self._set_states({"ct_inc":inc})

  def colder(self, inc = 20):
    self.warmer(-inc)

  def dim(self,inc = 25):
    self.brighter(-inc)

  def set_brightness(self,bri):
      self._set_states({"bri":int(bri)})

  def ison(self):
    return self._get_status()["state"]["any_on"]

  def maxima(self):
      return self._set_states({"on":True,"bri":254,'xy': [0.3691, 0.3719]})

  def nightlight(self):
      return self._set_states({"on":True,"bri":1,'xy': [0.5612, 0.4042]})


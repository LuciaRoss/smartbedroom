from requests import put,post,get,delete
import json

ip = "192.168.86.88"
uid = "glzhzFDLZ8Mcs-E7jgWWbtpY31xLQkY4RJoh7cxk"
apu = "http://"+ip+"/api/"+uid+"/"

def hget(url):
  return json.loads(get(apu+url).text)

def hpost(url,dic):
  return json.loads(post(apu+url,json=dic).text)

def hput(url,dic):
    print(dic)
    return json.loads(put(apu+url,json=dic).text)

def hdel(url):
  return json.loads(delete(apu+url).text)

def colorToHue(colorstring):
  #TODO
  colormap = {"red":0,"blue":46920,"green":25500}
  if colorstring in colormap:
    return colormap[colorstring]
  else:
    return 10000

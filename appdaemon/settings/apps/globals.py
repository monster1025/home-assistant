import importlib
import subprocess
from typing import Any, Tuple, Union

#
# Global module
# contain global functions
#
# Args:
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

"""Define various constants."""
CONF_PEOPLE = 'people'

def most_common(the_list: list) -> Any:
    """Return the most common element in a list."""
    return max(set(the_list), key=the_list.count)

def check_properties(self, args):
  missing = []
  for arg in args:
    if arg not in self.properties:
       missing.append(arg)
  if len(missing) > 0:
    self.error("Please provide {} in properties!".format(missing))
    return False
  return True

def check_args(self, args):
  missing = []
  for arg in args:
    if arg not in self.args:
       missing.append(arg)
  if len(missing) > 0:
    self.error("Please provide {} in config!".format(missing))
    return False
  return True

def get_group_entities(self, group):
    attributes = self.get_state(group, attribute = "all")
    if (attributes == None):
      self.log('Warning: Possible invalid group: {}'.format(group))
      return []
    if 'attributes' in attributes:
      attributes = attributes['attributes']

    #group
    if "entity_id" in attributes:
      return attributes["entity_id"]

    #simple item
    return [group]

def turn_on(self, entity_id, state):
  if entity_id.startswith("light"):
    self.call_service("light/turn_off", entity_id = entity_id, transition = 1, brightness = 255)
  else:
    self.turn_off(entity_id, state)

def turn_off(self, entity_id, state):
  if entity_id.startswith("light"):
    self.call_service("light/turn_off", entity_id = entity_id, transition = 1)
  else:
    self.turn_off(entity_id, state)

def notification(self, to, message):
  self.notify(message, name = "telegram")
  

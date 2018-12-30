import appdaemon.plugins.hass.hassapi as hass

#
# App to serve tags list via api call
#
# Args:
#
# secrets_file = path to secrets file
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class TagsList(hass.Hass):
  secrets_file = '/conf/secrets.yaml'
  def initialize(self):
    self.register_endpoint(self.api_call)
    if 'secrets_file' in self.args:
      self.secrets_file = self.args['secrets_file']

  def api_call(self, data):
    tags = []

    with open(self.secrets_file) as f:
      content = f.readlines()
      for line in content:
        if (line.startswith('tag_')):
          line = line.replace('\n','')
          tag = line.split(':')[1].strip()
          tags.append(tag)
    return tags, 200

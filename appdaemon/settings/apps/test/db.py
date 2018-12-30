import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

class Db(hass.Hass):
  def initialize(self):
    # Set up callback and listen for state change of desired switch
    self.listen_state(self.entity_changed, self.args["entity_id"])
    self.update_stats()

  def entity_changed(self, entity, attribute, old, new, kwargs):
    self.update_stats()

  def update_stats(self):
    engine = create_engine(self.args["connectionstring"])
    session_obj = sessionmaker(bind=engine)
    session = scoped_session(session_obj)

    results = session.execute('SELECT state,last_changed FROM states where entity_id = "' + self.args["entity_id"] + '" and state<>\'unknown\' and last_changed>=(NOW() - INTERVAL 1 MONTH) order by last_changed limit 1')
    row = results.first()
    start_value = float(row['state'])
    start_date = row['last_changed']

    current_value = float(self.get_state(self.args["entity_id"]))
    diff = round(current_value - start_value,2)
    self.log('Counter start value: {} (@{}), current value: {}, diff: {}'.format(start_value, start_date, current_value, diff))
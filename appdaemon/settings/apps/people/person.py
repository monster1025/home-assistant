import globals
from automation import Base
from globals import CONF_PEOPLE
from typing import Any, Tuple, Union
#
# Person
# Script that creates persons with their properties.
#
# Args:
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Person(Base):
    """Define a class to represent a person."""
    def initialize(self) -> None:
        """Initialize."""
        super().initialize()
        self._add_person_to_globals()
        # Listen for changes to the device trackers (to initiate re-rendering
        # if needed):
        for tracker in self.device_trackers:
            self.listen_state(self._device_tracker_changed_cb, tracker)

    @property
    def first_name(self) -> str:
        """Return the person's name."""
        return self.name.title()
    
    @property
    def device_trackers(self) -> list:
        """Return the device trackers associated with the person."""
        return self.properties['device_trackers']
    
    @property
    def notifiers(self) -> list:
        """Return the notifiers associated with the person."""
        return self.properties['notifiers']
    
    @property
    def presence_sensor(self) -> str:
        """Return the entity ID of the generated presence status sensor."""
        return 'sensor.{0}_presence_status'.format(self.name)
    
    @property
    def presence_input_select(self) -> str:
        """Return the input select related to the person's presence."""
        return self.properties['presence_input_select']

    @property
    def location(self) -> str:
        """Get the current location from combined device trackers."""
        raw_location = globals.most_common([
            self.get_tracker_state(tracker_entity)
            for tracker_entity in self.properties['device_trackers']
        ])

        if raw_location not in ('home', 'not_home'):
            return raw_location

        return self.get_state(self.presence_input_select)

        #return raw_location
        
    def _device_tracker_changed_cb(  # pylint: disable=too-many-arguments
            self, entity: Union[str, dict], attribute: str, old: str, new: str,
            kwargs: dict) -> None:
        """Respond when a device tracker changes state."""
        if new == old:
            return

        self._render_presence_status_sensor()

    def _add_person_to_globals(self):
        self.global_vars.setdefault(CONF_PEOPLE, [])

        existing_element = None
        for element in self.global_vars[CONF_PEOPLE]:
            if element.first_name == self.first_name:
                existing_element = element

        if existing_element == None:
            self.global_vars[CONF_PEOPLE].append(self)
        else:
            index = self.global_vars[CONF_PEOPLE].index(existing_element)
            self.global_vars[CONF_PEOPLE][index] = self

    def _render_presence_status_sensor(self):
        """Update the presence status sensor."""
        if self.location in ('Home', 'Just Arrived'):
            picture_state = 'home'
        else:
            picture_state = 'away'
        self.log('Setting presence sensor {} state to {}.'.format(self.presence_sensor, self.location))
        self.set_state(
            self.presence_sensor,
            state=self.location,
            attributes={
                'friendly_name':
                    self.first_name,
                'entity_picture':
                    '/local/{0}-{1}.png'.format(self.name, picture_state),
            })
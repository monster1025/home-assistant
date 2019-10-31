import appdaemon.plugins.hass.hassapi as hass
from notification import send_notification
import datetime
# from automation import Automation  # type: ignore

"""
Monitor events and output changes to the verbose_log. Nice for debugging purposes.
Arguments:
 - events: List of events to monitor
"""
class Test(hass.Hass):
    def initialize(self) -> None:
        self.log('test')
        # id = send_notification(
        #     self, targets="telegram_monster", message="Repeated message", title="title", when=datetime.datetime.now(), interval=10, iterations=2
        # )
        # self.log("id:{}".format(id))
        # id = send_notification(
        #     self, targets="telegram_monster", message="Dummy", title="title"
        # )

    def terminate(self):
        self.log('terminate')
        # for listen_event_handle in self.listen_event_handle_list:
        #     self.cancel_listen_event(listen_event_handle)
            
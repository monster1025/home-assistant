import appdaemon.plugins.hass.hassapi as hass

class TelegramTest(hass.Hass):
  def initialize(self):
      """Listen to Telegram Bot events of interest."""
      self.listen_event(self.receive_telegram_text, 'telegram_text')
      self.listen_event(self.receive_telegram_callback, 'telegram_callback')

  def receive_telegram_text(self, event_id, payload_event, *args):
      """Text repeater."""
      assert event_id == 'telegram_text'
      user_id = payload_event['user_id']
      msg = 'You said: ``` %s ```' % payload_event['text']
      keyboard = [[("Edit message", "/edit_msg"),
                   ("Don't", "/do_nothing")], 
                  [("Remove this button", "/remove button")]]
      self.call_service('telegram_bot/send_message',
                        title='*Dumb automation*',
                        target=user_id,
                        message=msg,
                        disable_notification=True,
                        inline_keyboard=keyboard)

  def receive_telegram_callback(self, event_id, payload_event, *args):
      """Event listener for Telegram callback queries."""
      assert event_id == 'telegram_callback'
      data_callback = payload_event['data']
      callback_id = payload_event['id']
      chat_id = payload_event['chat_id']
      self.log(payload_event)
      # keyboard = ["Edit message:/edit_msg, Don't:/do_nothing",
      #             "Remove this button:/remove button"]
      keyboard = [[("Edit message", "/edit_msg"),
                   ("Don't", "/do_nothing")],
                  [("Remove this button", "/remove button")]]

      if data_callback == '/edit_msg':  # Message editor:
          # Answer callback query
          self.call_service('telegram_bot/answer_callback_query',
                            message='Editing the message!',
                            callback_query_id=callback_id,
                            show_alert=True)

          # Edit the message origin of the callback query
          msg_id = payload_event['message']['message_id']
          user = payload_event['from_first']
          title = '*Message edit*'
          msg = 'Callback received from %s. Message id: %s. Data: ``` %s ```'
          self.call_service('telegram_bot/edit_message',
                            chat_id=chat_id,
                            message_id=msg_id,
                            title=title,
                            message=msg % (user, msg_id, data_callback),
                            inline_keyboard=keyboard)

      elif data_callback == '/remove button':  # Keyboard editor:
          # Answer callback query
          self.call_service('telegram_bot/answer_callback_query',
                            message='Callback received for editing the '
                                    'inline keyboard!',
                            callback_query_id=callback_id)

          # Edit the keyboard
          new_keyboard = keyboard[:1]
          self.call_service('telegram_bot/edit_replymarkup',
                            chat_id=chat_id,
                            message_id='last',
                            inline_keyboard=new_keyboard)

      elif data_callback == '/do_nothing':  # Only Answer to callback query
          self.call_service('telegram_bot/answer_callback_query',
                            message='OK, you said no!',
                            callback_query_id=callback_id)
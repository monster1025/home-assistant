import appdaemon.plugins.hass.hassapi as hass
import json

#
# Yandex.Alice integration
#
# Args:
#
# 
# 
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class YandexAlice(hass.Hass):

    def initialize(self):
        self.register_endpoint(self.api_call)
        self.sessionStorage = {}
        self.log('started')

    def api_call(self, request):
        # js = json.dumps(request, indent=4, sort_keys=True)
        # self.log('Request: %s' % js)

        response = {
            "version": request['version'],
            "session": request['session'],
            "response": {
                "end_session": False
            }
        }
        self.handle_dialog(request, response)

        # self.log('response: {}'.format(response['response']['text']))
        # js = json.dumps(response, indent=4, sort_keys=True)
        # self.log('Response: %s' % js)

        return response, 200
        
    # Функция для непосредственной обработки диалога.
    def handle_dialog(self, req, res):
        user_id = req['session']['user_id']
        command = req['request']['original_utterance'].lower()
        command_password = req['request']['command'].lower().replace(" ", "")
        password = "123456"
        self.log('command: {}'.format(command))

        if command == "ping":
            res['response']['text'] = 'pong =)'
            return

        if user_id not in self.sessionStorage:
            self.sessionStorage[user_id] = { 'auth': False }
            res['response']['text'] = 'Привет. Я могу управлять твоим домом. Для начала работы назови пароль.'
            return

        if command_password != password and self.sessionStorage[user_id]['auth'] == False:
            res['response']['text'] = 'Неправильный пароль: %s.' % command_password
            return

        # Обрабатываем ответ пользователя.
        if command_password == password and self.sessionStorage[user_id]['auth'] == False:
            self.sessionStorage[user_id]['auth'] = True
            res['response']['text'] = 'Вы авторизованы.'
            return

        self.handle_command(req, res)
        return

    # Функция возвращает две подсказки для ответа.
    def handle_command(self, req, res):
        user_id = req['session']['user_id']
        command = req['request']['original_utterance'].lower()
        command = command.replace('попроси управление домом', '').strip()
        command = command.replace('алиса', '').strip()
        isAuth = self.sessionStorage[user_id]['auth'] == True

        if not isAuth:
            res['response']['text'] = 'Вы не авторизованы.'
            return

        if command in ["включи свет", "включить свет"]:
            res['response']['text'] = 'Включаю свет.'
            self.turn_on("group.all_lights")
            self.turn_on("switch.kitchen_mini_light")
            return

        if command in ["включи свет в зале", "включить свет в зале","включи свет в гостинной", "включить свет в гостинной"]:
            res['response']['text'] = 'Свет включен.'
            self.turn_on("group.mainroom_light")
            return

        if command in ["выключи свет в зале", "выключить свет в зале","выключи свет в гостинной", "выключить свет в гостинной"]:
            res['response']['text'] = 'Свет выключен.'
            self.turn_off("group.mainroom_light")
            return

        if command in ["выключи свет", "выключить свет", "выключи весь свет"]:
            res['response']['text'] = 'Свет выключен.'
            self.turn_off("group.all_lights")
            self.turn_off("switch.kitchen_mini_light")
            return

        if command in ["хватит", "алиса, хватит", "алиса хватит", "отмена"]:
            res['response']['text'] = 'Хорошо'
            res['response']['end_session'] = True
            return

        if command in ["я ушел", "алиса я ушел"]:
            self.call_service("alarm_control_panel/alarm_arm_away", entity_id="alarm_control_panel.ha_alarm")
            res['response']['text'] = 'Приятной дороги.'
            return

        if command in ["я вернулся", "я пришёл", "я пришел"]:
            self.call_service("alarm_control_panel/alarm_disarm", entity_id="alarm_control_panel.ha_alarm")
            res['response']['text'] = 'Добро пожаловать домой.'
            return

        if command in ["запусти навык управление домом"]:
            res['response']['text'] = 'Уже запущен.'
            return

        res['response']['text'] = 'Извините, я не знаю команды %s.' % command
        return
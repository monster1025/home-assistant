#SHELL := /bin/bash

ARGS = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

lint:
	@echo "Checking python syntax with pyflakes"
	@pyflakes appdaemon

update_secrets_sample:
	@echo "Masking passwords..."
	#hass
	@cat hass/settings/secrets.yaml | sed "s/\:.*/\: xxxxxxxxx/g" > hass/settings/secrets.yaml.sample #mask passwords
	@sed -i "s/latitude:.*/latitude: 1.0/g" hass/settings/secrets.yaml.sample #must be a number
	@sed -i "s/longitude:.*/longitude: 1.0/g" hass/settings/secrets.yaml.sample #must be a number
	@sed -i "s/aqara1_mac:.*/aqara1_mac: xxxxxxxxxxxx/g" hass/settings/secrets.yaml.sample #len 12
	@sed -i "s/aqara1_key:.*/aqara1_key: xxxxxxxxxxxxxxxx/g" hass/settings/secrets.yaml.sample #len 16
	@sed -i "s/mirobot_key:.*/mirobot_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g" hass/settings/secrets.yaml.sample #len 32
	@sed -i "s/powerstrip_key:.*/powerstrip_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g" hass/settings/secrets.yaml.sample #len 32
	@sed -i "s/telegram_chat:.*/telegram_chat: 0/g" hass/settings/secrets.yaml.sample #must be a number
	@sed -i "s/timezone:.*/timezone: Europe\/London/g" hass/settings/secrets.yaml.sample #must be valid
	@sed -i "s/chat_id:.*/chat_id: 12312312/g" hass/settings/secrets.yaml.sample #must be valid
	@sed -i "s/purifier_key:.*/purifier_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g" hass/settings/secrets.yaml.sample #must be valid

	@echo "Masking env files..."
	@find . -name *.env | xargs -I{} cp {} {}.sample
	@find . -name *.env.sample | xargs -I{} sed -i "s/\=.*/\=xxxxxxxxx/g" {}

	@cat zigbee2mqtt/settings/configuration.yaml | sed "s/\:.*/\: xxxxxxxxx/g" > zigbee2mqtt/settings/configuration.yaml.sample #mask passwords

commit: update_secrets_sample
	git add .
	git commit -m "$(call ARGS,\"updating configuration\")"
	git push

%:
    @:

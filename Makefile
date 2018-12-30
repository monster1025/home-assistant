#SHELL := /bin/bash

ARGS = `arg="$(filter-out $@,$(MAKECMDGOALS))" && echo $${arg:-${1}}`

lint:
	@echo "Checking python syntax with pyflakes"
	@pyflakes appdaemon

update_secrets_sample:
	@echo "Masking passwords..."
	@cat secrets.yaml | sed "s/\:.*/\: xxxxxxxxx/g" > secrets.yaml.sample #mask passwords
	@sed -i "s/latitude:.*/latitude: 1.0/g" secrets.yaml.sample #must be a number
	@sed -i "s/longitude:.*/longitude: 1.0/g" secrets.yaml.sample #must be a number
	@sed -i "s/aqara1_mac:.*/aqara1_mac: xxxxxxxxxxxx/g" secrets.yaml.sample #len 12
	@sed -i "s/aqara1_key:.*/aqara1_key: xxxxxxxxxxxxxxxx/g" secrets.yaml.sample #len 16
	@sed -i "s/mirobot_key:.*/mirobot_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g" secrets.yaml.sample #len 32
	@sed -i "s/powerstrip_key:.*/powerstrip_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/g" secrets.yaml.sample #len 32
	@sed -i "s/telegram_chat:.*/telegram_chat: 0/g" secrets.yaml.sample #must be a number
	@sed -i "s/timezone:.*/timezone: Europe\/London/g" secrets.yaml.sample #must be valid

commit: update_secrets_sample
	git add .
	git commit -m "$(call ARGS,\"updating configuration\")"
	git push

%:
    @:

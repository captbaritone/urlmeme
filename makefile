SHELL=/bin/bash

.PHONY: local deploy

local:
	python url.py

deploy:
	cat scripts/deploy.sh | ssh jordaneldredge.com DEPLOYER=`whoami` sh; \

test:
	python tests.py
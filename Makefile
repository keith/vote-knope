PORT=1234

.PHONY: ngrok serve setup verify

setup:
	brew install ngrok
	pip install -r requirements.txt

ngrok:
	ngrok -subdomain=webhook $(PORT)

serve: verify
	python main.py $(PORT)

verify: \
	guard-hook_secret \
	guard-github_user \
	guard-github_pass

guard-%:
	@ if [ "${${*}}" == "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

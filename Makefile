

SHELL=/bin/bash



build: install
	bundle exec jekyll build $(config) $(dest)

serve: install
	bundle exec jekyll serve $(config) --port 8001

.PHONY: install build serve

format:
	black .
	isort --profile black .

local-site:
	jekyll serve -l -H localhost

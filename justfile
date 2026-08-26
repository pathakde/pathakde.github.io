black := `which black` # `black` is required
isort := `which isort` # `isort` is required
jekyll := `which jekyll` # `jekyll` is required

format:
	black .
	isort --profile black .

dev:
	bundle exec jekyll serve --watch --live --future

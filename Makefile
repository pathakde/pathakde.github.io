env:
	conda env create -f environment.yml

export:
	conda env export --from-history --no-builds | grep -v "^prefix: " | sed '1s/^name: base$$/name: dpsite/' > environment.yml

format:
	black .
	isort --profile black .

local-site:
	jekyll serve -l -H localhost

figures:
	python scripts/compile_pub_images.py

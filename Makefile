env:
	conda env create -f environment.yml

export:
	conda env export --from-history --no-builds | grep -v "^prefix: " > environment.yml

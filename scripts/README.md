# Setup
```bash
# checked on python3.13

# install packages into .venv
make install

# activate .venv
source .venv/bin/activate

# run script [example]
python cv_markdown_to_json.py
```

# Remember to freeze requirements after installing new packages
```bash
source .venv/bin/activate
pip install [package]
make freeze
```

# Format
```bash
source .venv/bin/activate

black {}
isort --profile black {}
```
TODO: learn to use uv
TODO: move python dependency management to root

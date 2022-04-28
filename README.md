# solomon-ingestor

A data ingester of Yugioh cards from [YGOPRODECK](https://ygoprodeck.com/) along with their japanese name scraping from [https://yugioh.fandom.com/wiki/Yu-Gi-Oh!] to store in elasticsearch.

## For development

### Setup development environment

```sh
virtualenv venv
# For fish
source venv/bin/activate.fish
# For shell
source venv/bin/activate
pip install -r requirements.txt
```

### Running on local
```sh
# Run on machine
python src/main.py
```

### Release
```sh
earthly --build-arg TAG=<TAG> --push +release
```

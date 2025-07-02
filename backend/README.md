Ative o ambiente virtual

Windows: 
```
\.venv\Scripts\Activate.ps1
```

Linux:
```
source .venv/bin/activate
```

Configure um arquivo .env dentro da pasta backend com as seguintes configuracoes
```
POSTGRES_PASSWORD=<yoursecurepassword>
POSTGRES_USER=<youruser>
POSTGRES_DB=<yourdb>

DB_USER=<youruser>
DB_NAME=<yourdb>
DB_PASSWORD=<yoursecurepassword>
DB_HOST=localhost
```


Depois execute
```
pip install -r requirements.txt
```

Inicie o docker
```
docker compose up -d
```

Para rodar a API
```
python run.py
```

Para parar os containers
```
docker compose down
```
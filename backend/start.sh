#!/bin/bash

echo "Inserindo dados na Qdrant..."
python -m scripts.inserir_na_qdrant

echo "Populando o banco de dados..."
python -m scripts.seed_database

echo "Iniciando o servidor Flask..."
python run.py

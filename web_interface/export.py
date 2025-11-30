# Exportação de Resultados
import csv
import json
from web_interface.database import Database

def export_to_csv(file_path):
    """Exporta os logs para um arquivo CSV.

    Args:
        file_path (str): Caminho para o arquivo CSV.
    """
    db = Database()
    logs = db.fetch_logs()
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Prompt", "Response", "Timestamp"])
        writer.writerows(logs)

def export_to_json(file_path):
    """Exporta os logs para um arquivo JSON.

    Args:
        file_path (str): Caminho para o arquivo JSON.
    """
    db = Database()
    logs = db.fetch_logs()
    data = [
        {"ID": log[0], "Prompt": log[1], "Response": log[2], "Timestamp": log[3]} for log in logs
    ]
    with open(file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False, indent=4)

# Exemplo de uso
if __name__ == "__main__":
    export_to_csv("data/logs.csv")
    export_to_json("data/logs.json")
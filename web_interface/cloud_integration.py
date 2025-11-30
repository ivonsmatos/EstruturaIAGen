# Integração com Serviços de Nuvem
import boto3

def upload_to_s3(file_path, bucket_name, object_name=None):
    """Faz upload de um arquivo para um bucket S3.

    Args:
        file_path (str): Caminho do arquivo local.
        bucket_name (str): Nome do bucket S3.
        object_name (str): Nome do objeto no S3 (opcional).
    """
    if object_name is None:
        object_name = file_path

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"Arquivo {file_path} enviado para {bucket_name}/{object_name}.")
    except Exception as e:
        print(f"Erro ao enviar arquivo para S3: {e}")

# Exemplo de uso
if __name__ == "__main__":
    upload_to_s3("data/logs.json", "meu-bucket", "logs.json")
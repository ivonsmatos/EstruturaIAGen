from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def export_data():
    # Simulação de exportação de dados
    with open('exported_data.csv', 'w') as f:
        f.write('id,name,value\n1,example,100')
    return 'Exportação concluída!'
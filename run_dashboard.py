#!/usr/bin/env python
"""Script para testar imports e iniciar dashboard"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
root_path = Path(__file__).parent
sys.path.insert(0, str(root_path))

print(f"✓ Python path: {sys.path[0]}")

# Testar imports
try:
    from app.export import export_manager
    print("✓ Export manager importado")
except Exception as e:
    print(f"✗ Erro ao importar export_manager: {e}")
    sys.exit(1)

try:
    from app.analysis import drilldown_analyzer
    print("✓ Drill-down analyzer importado")
except Exception as e:
    print(f"✗ Erro ao importar drilldown_analyzer: {e}")
    sys.exit(1)

try:
    from app.themes import theme_manager
    print("✓ Theme manager importado")
except Exception as e:
    print(f"✗ Erro ao importar theme_manager: {e}")
    sys.exit(1)

print("\n✅ Todos os imports OK!")
print("Iniciando dashboard...")

# Importar dashboard
sys.path.insert(0, str(root_path / "web_interface"))
from dashboard_profissional import app

if __name__ == '__main__':
    print(f"🚀 Dashboard rodando em http://127.0.0.1:8050")
    app.run(debug=False, host='127.0.0.1', port=8050)

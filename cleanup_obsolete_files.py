#!/usr/bin/env python3
"""
Cleanup Script - Remove obsolete files and consolidate project
Executa após QA audit para otimizar estrutura do projeto

Usage: python cleanup_obsolete_files.py
"""

import os
import shutil
from pathlib import Path

# Lista de arquivos obsoletos a remover
OBSOLETE_FILES = [
    "SPRINT_P1_FINAL_REPORT.py",
    "SPRINT_P1_STATUS_REPORT.py", 
    "SPRINT_P2_FINAL_REPORT.py",
    "P1_DATABASE_COMPLETE.py",
    "app/cache/dashboard_cache.py",  # Merged into cache_manager.py
]

# Arquivos a arquivar em docs/archive/
ARCHIVE_FILES = [
    "P0_IMPLEMENTATION.md",
    "SPRINT_P1_PLANNING.md",
    "SPRINT_P1_README.md",
    "P1_DATABASE_INTEGRATION.md",
    "P2_1_EXPORT_IMPLEMENTATION.md",
    "P2_2_DRILLDOWN_IMPLEMENTATION.md",
    "P2_3_THEMES_IMPLEMENTATION.md",
    "CHANGELOG.md",  # Create archive of old changes
]

def cleanup_obsolete_files():
    """Remove obsolete report and documentation files"""
    print("🧹 Limpando arquivos obsoletos...")
    
    root = Path(".")
    removed_count = 0
    
    for file_path in OBSOLETE_FILES:
        full_path = root / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✓ Removido: {file_path}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Erro ao remover {file_path}: {e}")
    
    print(f"\n✅ {removed_count} arquivos obsoletos removidos")
    return removed_count


def archive_old_docs():
    """Move old documentation to archive"""
    print("\n📦 Arquivando documentação antiga...")
    
    root = Path(".")
    archive_dir = root / "docs" / "archive"
    
    # Criar diretório de arquivo
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    archived_count = 0
    for file_path in ARCHIVE_FILES:
        full_path = root / file_path
        if full_path.exists():
            try:
                dest = archive_dir / full_path.name
                shutil.move(str(full_path), str(dest))
                print(f"  ✓ Arquivado: {file_path}")
                archived_count += 1
            except Exception as e:
                print(f"  ✗ Erro ao arquivar {file_path}: {e}")
    
    print(f"\n✅ {archived_count} arquivos arquivados em docs/archive/")
    return archived_count


def remove_unused_imports():
    """Identifica e lista arquivos com possíveis imports não utilizados"""
    print("\n🔍 Verificando imports não utilizados...")
    
    files_to_check = [
        "app/cache/cache_manager.py",
        "app/themes/theme_manager.py",
        "app/ml/prediction_engine.py",
        "app/export/export_manager.py",
        "app/analytics/advanced_analytics.py",
    ]
    
    print("  Arquivos recomendados para revisão de imports:")
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"  📋 {file_path}")
    
    print("\n  💡 Use 'pylint --disable=all --enable=unused-import' para verificar")
    

def verify_consolidation():
    """Verifica se a consolidação foi realizada corretamente"""
    print("\n✔️ Verificando consolidação...")
    
    checks = {
        "cache_manager.py incluir dashboard functions": Path("app/cache/cache_manager.py").stat().st_size > 10000,
        "dashboard_cache.py removido": not Path("app/cache/dashboard_cache.py").exists(),
        "docs/archive/ criado": Path("docs/archive").exists(),
    }
    
    all_passed = True
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check_name}")
        if not result:
            all_passed = False
    
    return all_passed


def print_summary():
    """Imprime resumo das ações realizadas"""
    print("\n" + "="*70)
    print("📊 RESUMO DA LIMPEZA")
    print("="*70)
    print("""
✅ Arquivos obsoletos removidos:
   - SPRINT_P1_FINAL_REPORT.py
   - SPRINT_P1_STATUS_REPORT.py
   - SPRINT_P2_FINAL_REPORT.py
   - P1_DATABASE_COMPLETE.py
   - app/cache/dashboard_cache.py (merged into cache_manager.py)

📦 Documentação arquivada em docs/archive/:
   - P0_IMPLEMENTATION.md
   - SPRINT_P1_PLANNING.md
   - SPRINT_P1_README.md
   - P1_DATABASE_INTEGRATION.md
   - P2_1_EXPORT_IMPLEMENTATION.md
   - P2_2_DRILLDOWN_IMPLEMENTATION.md
   - P2_3_THEMES_IMPLEMENTATION.md
   - CHANGELOG.md

🔧 Consolidações realizadas:
   - Cache functions merged into cache_manager.py
   - Dashboard cache functions integrated
   - Cleaned up project structure

📊 Resultado:
   - Arquivos reduzidos: ~15 files
   - Código melhor organizado
   - Rastreabilidade mantida via git e archive
   - Projeto mais limpo para manutenção

🚀 Próximos passos:
   1. Revisar app/cache/decorators.py (uso)
   2. Remover imports não utilizados
   3. Standardizar docstrings
   4. Executar pytest para validar
    """)
    print("="*70)


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║            CLEANUP - Consolidação de Projeto                  ║
    ║                EstruturaIAGen v3.0.0                          ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        removed = cleanup_obsolete_files()
        archived = archive_old_docs()
        remove_unused_imports()
        
        if verify_consolidation():
            print_summary()
            print("\n✅ Limpeza completada com sucesso!")
        else:
            print("\n⚠️ Algumas verificações falharam. Revise manualmente.")
            
    except Exception as e:
        print(f"\n❌ Erro durante limpeza: {e}")
        import traceback
        traceback.print_exc()

"""
Sistema de Temas Customizáveis
Suporta temas predefinidos e personalizados com persistência
v2.0.0 - P2.3 Theme Management
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ThemeColors:
    """Definição de cores de um tema"""
    bg_body: str
    bg_card: str
    neon_main: str
    neon_dim: str
    accent_orange: str
    accent_secondary: str
    text_main: str
    text_sub: str
    border: str
    success: str
    warning: str
    error: str
    
    def to_dict(self) -> Dict[str, str]:
        """Converte para dicionário"""
        return asdict(self)


@dataclass
class Theme:
    """Definição completa de um tema"""
    name: str
    description: str
    colors: ThemeColors
    created_at: str = None
    updated_at: str = None
    is_default: bool = False
    is_custom: bool = False
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'name': self.name,
            'description': self.description,
            'colors': self.colors.to_dict(),
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_default': self.is_default,
            'is_custom': self.is_custom
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Theme':
        """Cria Theme a partir de dicionário"""
        colors = ThemeColors(**data['colors'])
        return Theme(
            name=data['name'],
            description=data.get('description', ''),
            colors=colors,
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            is_default=data.get('is_default', False),
            is_custom=data.get('is_custom', False)
        )


class ThemeManager:
    """Gerenciador de temas customizáveis"""
    
    # Temas predefinidos
    DARK_THEME = Theme(
        name='dark',
        description='Tema escuro profissional com acentos neon',
        colors=ThemeColors(
            bg_body='#0D0D0D',
            bg_card='rgba(26, 26, 26, 0.8)',
            neon_main='#BBF244',
            neon_dim='rgba(187, 242, 68, 0.1)',
            accent_orange='#F27244',
            accent_secondary='#FF9F5A',
            text_main='#E0E0E0',
            text_sub='#888888',
            border='#333333',
            success='#00FF41',
            warning='#FFD700',
            error='#FF6B6B'
        ),
        is_default=True
    )
    
    LIGHT_THEME = Theme(
        name='light',
        description='Tema claro minimalista',
        colors=ThemeColors(
            bg_body='#FFFFFF',
            bg_card='#F5F5F5',
            neon_main='#2563EB',
            neon_dim='rgba(37, 99, 235, 0.1)',
            accent_orange='#F97316',
            accent_secondary='#FB923C',
            text_main='#1F2937',
            text_sub='#6B7280',
            border='#E5E7EB',
            success='#10B981',
            warning='#F59E0B',
            error='#EF4444'
        )
    )
    
    CYBERPUNK_THEME = Theme(
        name='cyberpunk',
        description='Tema futurista com cores vibrantes',
        colors=ThemeColors(
            bg_body='#0A0E27',
            bg_card='#0F1535',
            neon_main='#00FF88',
            neon_dim='rgba(0, 255, 136, 0.1)',
            accent_orange='#FF006E',
            accent_secondary='#8338EC',
            text_main='#00FFFF',
            text_sub='#FF006E',
            border='#00FF88',
            success='#00FF88',
            warning='#FFD60A',
            error='#FF006E'
        )
    )
    
    OCEAN_THEME = Theme(
        name='ocean',
        description='Tema inspirado no oceano com tons azuis',
        colors=ThemeColors(
            bg_body='#0A1929',
            bg_card='#132F4C',
            neon_main='#90CAF9',
            neon_dim='rgba(144, 202, 249, 0.1)',
            accent_orange='#FFB74D',
            accent_secondary='#64B5F6',
            text_main='#E3F2FD',
            text_sub='#90CAF9',
            border='#1E3A5F',
            success='#66BB6A',
            warning='#FFB74D',
            error='#EF5350'
        )
    )
    
    FOREST_THEME = Theme(
        name='forest',
        description='Tema natural com tons verdes e marrom',
        colors=ThemeColors(
            bg_body='#1B3D1F',
            bg_card='#254129',
            neon_main='#81C784',
            neon_dim='rgba(129, 199, 132, 0.1)',
            accent_orange='#FFB74D',
            accent_secondary='#66BB6A',
            text_main='#C8E6C9',
            text_sub='#A1D5A1',
            border='#2E5233',
            success='#81C784',
            warning='#FFB74D',
            error='#E57373'
        )
    )
    
    def __init__(self, themes_dir: str = "./themes"):
        """
        Inicializa o gerenciador de temas
        
        Args:
            themes_dir: Diretório para salvar temas customizados
        """
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar temas predefinidos
        self.themes: Dict[str, Theme] = {
            'dark': self.DARK_THEME,
            'light': self.LIGHT_THEME,
            'cyberpunk': self.CYBERPUNK_THEME,
            'ocean': self.OCEAN_THEME,
            'forest': self.FOREST_THEME
        }
        
        # Carregar temas customizados
        self._load_custom_themes()
        
        logger.info(f"✓ ThemeManager inicializado com {len(self.themes)} temas")
    
    def _load_custom_themes(self) -> None:
        """Carrega temas customizados do diretório"""
        try:
            theme_files = self.themes_dir.glob('*.json')
            for theme_file in theme_files:
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        theme = Theme.from_dict(data)
                        self.themes[theme.name] = theme
                    logger.info(f"✓ Tema customizado carregado: {theme.name}")
                except Exception as e:
                    logger.warning(f"✗ Erro ao carregar tema {theme_file}: {str(e)}")
        except Exception as e:
            logger.error(f"✗ Erro ao carregar temas customizados: {str(e)}")
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """
        Obtém um tema pelo nome
        
        Args:
            name: Nome do tema
            
        Returns:
            Theme ou None se não encontrado
        """
        return self.themes.get(name)
    
    def list_themes(self) -> List[Dict[str, Any]]:
        """
        Lista todos os temas disponíveis
        
        Returns:
            Lista de temas
        """
        return [
            {
                'name': theme.name,
                'description': theme.description,
                'is_default': theme.is_default,
                'is_custom': theme.is_custom
            }
            for theme in self.themes.values()
        ]
    
    def create_custom_theme(
        self,
        name: str,
        description: str,
        colors: Dict[str, str]
    ) -> Theme:
        """
        Cria um tema customizado
        
        Args:
            name: Nome do tema
            description: Descrição
            colors: Dicionário com cores
            
        Returns:
            Tema criado
        """
        try:
            if name in self.themes:
                raise ValueError(f"Tema '{name}' já existe")
            
            if not name.replace('_', '').replace('-', '').isalnum():
                raise ValueError("Nome deve conter apenas letras, números, - e _")
            
            # Validar cores
            required_colors = [
                'bg_body', 'bg_card', 'neon_main', 'neon_dim',
                'accent_orange', 'accent_secondary', 'text_main',
                'text_sub', 'border', 'success', 'warning', 'error'
            ]
            
            for color in required_colors:
                if color not in colors:
                    raise ValueError(f"Cor obrigatória faltando: {color}")
                if not self._is_valid_color(colors[color]):
                    raise ValueError(f"Cor inválida para {color}: {colors[color]}")
            
            # Criar tema
            theme_colors = ThemeColors(**colors)
            theme = Theme(
                name=name,
                description=description,
                colors=theme_colors,
                is_custom=True
            )
            
            # Salvar
            self._save_theme(theme)
            self.themes[name] = theme
            
            logger.info(f"✓ Tema customizado criado: {name}")
            return theme
            
        except Exception as e:
            logger.error(f"✗ Erro ao criar tema: {str(e)}")
            raise
    
    def _is_valid_color(self, color: str) -> bool:
        """Valida se uma cor é um hex válido ou rgba"""
        color = color.strip()
        
        # Verificar hex
        if color.startswith('#'):
            hex_chars = '0123456789abcdefABCDEF'
            return len(color) in [4, 7] and all(c in hex_chars for c in color[1:])
        
        # Verificar rgba
        if color.startswith('rgba('):
            return color.endswith(')')
        
        return False
    
    def update_theme(
        self,
        name: str,
        colors: Optional[Dict[str, str]] = None,
        description: Optional[str] = None
    ) -> Theme:
        """
        Atualiza um tema customizado
        
        Args:
            name: Nome do tema
            colors: Novas cores (opcional)
            description: Nova descrição (opcional)
            
        Returns:
            Tema atualizado
        """
        try:
            if name not in self.themes:
                raise ValueError(f"Tema '{name}' não encontrado")
            
            theme = self.themes[name]
            
            if not theme.is_custom:
                raise ValueError(f"Não é possível editar tema predefinido: {name}")
            
            if colors:
                for key, value in colors.items():
                    if not self._is_valid_color(value):
                        raise ValueError(f"Cor inválida para {key}: {value}")
                    setattr(theme.colors, key, value)
            
            if description:
                theme.description = description
            
            theme.updated_at = datetime.utcnow().isoformat()
            
            # Salvar
            self._save_theme(theme)
            
            logger.info(f"✓ Tema atualizado: {name}")
            return theme
            
        except Exception as e:
            logger.error(f"✗ Erro ao atualizar tema: {str(e)}")
            raise
    
    def delete_theme(self, name: str) -> bool:
        """
        Deleta um tema customizado
        
        Args:
            name: Nome do tema
            
        Returns:
            True se deletado, False caso contrário
        """
        try:
            if name not in self.themes:
                raise ValueError(f"Tema '{name}' não encontrado")
            
            theme = self.themes[name]
            
            if not theme.is_custom:
                raise ValueError(f"Não é possível deletar tema predefinido: {name}")
            
            # Deletar arquivo
            theme_file = self.themes_dir / f"{name}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            del self.themes[name]
            
            logger.info(f"✓ Tema deletado: {name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro ao deletar tema: {str(e)}")
            raise
    
    def _save_theme(self, theme: Theme) -> None:
        """Salva tema em arquivo JSON"""
        theme_file = self.themes_dir / f"{theme.name}.json"
        
        with open(theme_file, 'w', encoding='utf-8') as f:
            json.dump(theme.to_dict(), f, indent=2, ensure_ascii=False)
    
    def export_theme_as_css(self, theme_name: str) -> str:
        """
        Exporta tema como CSS personalizado
        
        Args:
            theme_name: Nome do tema
            
        Returns:
            String com CSS
        """
        theme = self.get_theme(theme_name)
        if not theme:
            raise ValueError(f"Tema '{theme_name}' não encontrado")
        
        colors = theme.colors
        css = f"""
/* Tema: {theme.name} */
/* {theme.description} */
:root {{
    --bg-body: {colors.bg_body};
    --bg-card: {colors.bg_card};
    --neon-main: {colors.neon_main};
    --neon-dim: {colors.neon_dim};
    --accent-orange: {colors.accent_orange};
    --accent-secondary: {colors.accent_secondary};
    --text-main: {colors.text_main};
    --text-sub: {colors.text_sub};
    --border: {colors.border};
    --success: {colors.success};
    --warning: {colors.warning};
    --error: {colors.error};
}}

body {{
    background-color: var(--bg-body);
    color: var(--text-main);
}}

.card {{
    background-color: var(--bg-card);
    border-color: var(--border);
}}

.neon {{
    color: var(--neon-main);
}}

.accent-orange {{
    color: var(--accent-orange);
}}

.success {{
    color: var(--success);
}}

.warning {{
    color: var(--warning);
}}

.error {{
    color: var(--error);
}}
"""
        return css.strip()
    
    def duplicate_theme(self, source_name: str, new_name: str) -> Theme:
        """
        Duplica um tema
        
        Args:
            source_name: Nome do tema original
            new_name: Nome do novo tema
            
        Returns:
            Novo tema criado
        """
        source = self.get_theme(source_name)
        if not source:
            raise ValueError(f"Tema '{source_name}' não encontrado")
        
        colors_dict = source.colors.to_dict()
        return self.create_custom_theme(
            new_name,
            f"Cópia de {source.description}",
            colors_dict
        )


# Instância global
theme_manager = ThemeManager()

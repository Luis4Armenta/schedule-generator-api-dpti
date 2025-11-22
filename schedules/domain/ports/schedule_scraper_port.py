from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

class ScheduleScraperPort(ABC):
    """Puerto (interfaz) para scrapers de horarios - Arquitectura Hexagonal
    
    Define el contrato que deben cumplir los adaptadores externos que obtengan
    información de horarios desde sistemas externos (SAES, APIs, etc.)
    """
    
    @abstractmethod
    def download_schedules(
        self,
        career: str,
        career_plan: str,
        plan_periods: List[int],
        shift: Optional[str] = None,
        sequence: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Descarga horarios completos desde el sistema externo
        
        Args:
            career: Código de carrera
            career_plan: Código del plan de estudios
            plan_periods: Lista de períodos (1-10)
            shift: Turno específico (opcional)
            sequence: Secuencia específica (opcional)
            
        Returns:
            Lista de diccionarios con información de cursos:
            {
                'sequence': str,
                'subject': str,
                'teacher': str,
                'schedule': List[Dict],
                'plan': str,
                'level': str,
                'career': str,
                'shift': str,
                'semester': str,
                'required_credits': float,
                'teacher_positive_score': float
            }
        """
        pass
    
    @abstractmethod
    def download_availability(
        self,
        career: str,
        career_plan: str
    ) -> List[Dict[str, Any]]:
        """Descarga disponibilidad de cursos desde el sistema externo
        
        Args:
            career: Código de carrera
            career_plan: Código del plan de estudios
            
        Returns:
            Lista de diccionarios con disponibilidad:
            {
                'sequence': str,
                'subject': str,
                'availability': int
            }
        """
        pass

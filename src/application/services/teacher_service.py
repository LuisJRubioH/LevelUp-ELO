from src.infrastructure.external_api.ai_client import get_pedagogical_analysis

class TeacherService:
    """
    Servicio de aplicación que orquesta los casos de uso del profesor.
    """
    def __init__(self, repository):
        self.repository = repository

    def get_dashboard_data(self, teacher_id):
        """Recupera datos consolidados para el dashboard del profesor."""
        students = self.repository.get_students_by_teacher(teacher_id)
        groups = self.repository.get_groups_by_teacher(teacher_id)
        return students, groups

    def get_student_report(self, student_id):
        """Genera un reporte detallado de un estudiante."""
        attempts = self.repository.get_student_attempts_detail(student_id)
        # Aquí se podrían añadir cálculos adicionales de dominio
        return attempts

    def generate_ai_analysis(self, student_id, global_elo, api_key=None):
        """Orquesta la generación del análisis pedagógico con IA."""
        attempts = self.repository.get_student_attempts_detail(student_id)
        if not attempts:
            return "No hay suficientes datos para analizar."

        recent_attempts = attempts[-10:]
        recent_acc = sum(1 for a in recent_attempts if a['is_correct']) / len(recent_attempts) if recent_attempts else 0
        topics_unique = list(set([a['topic'] for a in attempts]))

        student_data = {
            "elo_global": global_elo,
            "attempts_count": len(attempts),
            "topics": topics_unique,
            "recent_accuracy": recent_acc
        }

        return get_pedagogical_analysis(student_data, api_key=api_key)

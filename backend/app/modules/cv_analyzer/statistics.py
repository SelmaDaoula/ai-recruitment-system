"""
Module de statistiques avancées pour l'analyse de CV
"""

import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.candidate import Candidate
from app.models.job_offer import JobOffer

logger = logging.getLogger(__name__)


class RecruitmentStats:
    """
    Générateur de statistiques pour le recrutement
    """
    
    @staticmethod
    def get_job_statistics(db: Session, job_id: int) -> Dict:
        """
        Statistiques complètes pour une offre d'emploi
        
        Args:
            db: Session de base de données
            job_id: ID de l'offre
        
        Returns:
            dict: Statistiques détaillées
        """
        candidates = db.query(Candidate).filter(Candidate.job_offer_id == job_id).all()
        
        if not candidates:
            return {
                "total_candidates": 0,
                "message": "Aucun candidat pour cette offre"
            }
        
        scores = [c.cv_score for c in candidates if c.cv_score]
        
        # Catégories
        category_a = [c for c in candidates if c.cv_score >= 80]
        category_b = [c for c in candidates if 65 <= c.cv_score < 80]
        category_c = [c for c in candidates if 50 <= c.cv_score < 65]
        category_d = [c for c in candidates if c.cv_score < 50]
        
        # Compétences les plus fréquentes
        all_skills = {}
        for c in candidates:
            if c.extracted_data and 'skills' in c.extracted_data:
                for skill in c.extracted_data['skills']:
                    all_skills[skill] = all_skills.get(skill, 0) + 1
        
        # Top 10 compétences
        top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:10]
        
        stats = {
            "total_candidates": len(candidates),
            "scores": {
                "average": round(sum(scores) / len(scores), 1) if scores else 0,
                "min": min(scores) if scores else 0,
                "max": max(scores) if scores else 0,
                "median": sorted(scores)[len(scores)//2] if scores else 0
            },
            "categories": {
                "A (≥80)": {
                    "count": len(category_a),
                    "percentage": round(len(category_a) / len(candidates) * 100, 1),
                    "candidates": [f"{c.first_name} {c.last_name}" for c in category_a[:5]]
                },
                "B (65-79)": {
                    "count": len(category_b),
                    "percentage": round(len(category_b) / len(candidates) * 100, 1)
                },
                "C (50-64)": {
                    "count": len(category_c),
                    "percentage": round(len(category_c) / len(candidates) * 100, 1)
                },
                "D (<50)": {
                    "count": len(category_d),
                    "percentage": round(len(category_d) / len(candidates) * 100, 1)
                }
            },
            "top_skills": [
                {"skill": skill, "count": count, "percentage": round(count/len(candidates)*100, 1)}
                for skill, count in top_skills
            ],
            "recommendations": {
                "to_interview": len(category_a),
                "to_consider": len(category_b),
                "reserve": len(category_c),
                "reject": len(category_d)
            }
        }
        
        logger.info(f"📊 Statistiques générées pour offre #{job_id}")
        
        return stats
    
    @staticmethod
    def get_candidate_comparison(db: Session, candidate_id: int, job_id: int) -> Dict:
        """
        Compare un candidat avec les autres pour la même offre
        
        Args:
            db: Session
            candidate_id: ID du candidat
            job_id: ID de l'offre
        
        Returns:
            dict: Comparaison
        """
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return {"error": "Candidat introuvable"}
        
        all_candidates = db.query(Candidate).filter(Candidate.job_offer_id == job_id).all()
        
        # Rang du candidat
        sorted_candidates = sorted(all_candidates, key=lambda x: x.cv_score, reverse=True)
        rank = next((i+1 for i, c in enumerate(sorted_candidates) if c.id == candidate_id), None)
        
        # Scores moyens
        avg_score = sum(c.cv_score for c in all_candidates) / len(all_candidates)
        
        # Percentile
        better_than = sum(1 for c in all_candidates if c.cv_score < candidate.cv_score)
        percentile = round(better_than / len(all_candidates) * 100, 1)
        
        return {
            "candidate": {
                "name": f"{candidate.first_name} {candidate.last_name}",
                "score": candidate.cv_score
            },
            "ranking": {
                "position": rank,
                "total": len(all_candidates),
                "percentile": percentile
            },
            "comparison": {
                "average_score": round(avg_score, 1),
                "difference": round(candidate.cv_score - avg_score, 1),
                "above_average": candidate.cv_score > avg_score
            }
        }
    
    @staticmethod
    def get_global_statistics(db: Session) -> Dict:
        """
        Statistiques globales du système
        
        Args:
            db: Session
        
        Returns:
            dict: Stats globales
        """
        total_jobs = db.query(JobOffer).count()
        total_candidates = db.query(Candidate).count()
        
        active_jobs = db.query(JobOffer).filter(JobOffer.is_active == True).count()
        
        avg_score = db.query(func.avg(Candidate.cv_score)).scalar()
        
        # Candidats par catégorie (global)
        category_a = db.query(Candidate).filter(Candidate.cv_score >= 80).count()
        category_b = db.query(Candidate).filter(
            Candidate.cv_score >= 65, 
            Candidate.cv_score < 80
        ).count()
        
        return {
            "system": {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "total_candidates": total_candidates,
                "average_score": round(avg_score, 1) if avg_score else 0
            },
            "quality": {
                "excellent_candidates": category_a,
                "good_candidates": category_b,
                "excellent_percentage": round(category_a/total_candidates*100, 1) if total_candidates else 0
            }
        }


# ============ Test des statistiques ============

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MODULE DE STATISTIQUES")
    print("="*60)
    print("\nCe module fournit des statistiques avancées :")
    print("  • Statistiques par offre d'emploi")
    print("  • Comparaison de candidats")
    print("  • Statistiques globales du système")
    print("  • Top compétences")
    print("  • Distribution par catégories")
    print("\n" + "="*60 + "\n")
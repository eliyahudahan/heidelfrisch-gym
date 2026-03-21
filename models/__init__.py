"""
HeidelFrisch Gym – Models Package
==================================
Makes all models easily accessible
"""

from .alnatura_model import spoilage_rate_alnatura, risk_score_from_spoilage

__all__ = ['spoilage_rate_alnatura', 'risk_score_from_spoilage']

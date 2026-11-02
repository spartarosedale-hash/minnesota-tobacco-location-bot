"""Combine research demographic signals WITHOUT double-counting marginals.

Independent age/sex/income marginal estimates are alternate views, NOT
independent probabilities. No product-user totals may be added across
cigarettes, vaping, cigars or smokeless because dual use is possible.
A calibrated joint rate requires actual age x sex x income x geography
survey cells or a fitted, validated model. This module does not invent them.
"""
from dataclasses import dataclass, field
from typing import Mapping

@dataclass(frozen=True)
class DemographicEvidence:
    product: str
    source: str
    source_year: int
    estimated_users: float
    population_covered: int
    dimension: str
    geography: str = "United States"
    def __post_init__(self):
        if not self.product or not self.source or not self.dimension:
            raise ValueError("Evidence needs product, source and dimension")
        if self.population_covered <= 0 or not 0 <= self.estimated_users <= self.population_covered:
            raise ValueError("Invalid population or estimate")

@dataclass(frozen=True)
class ProductAssessment:
    product: str
    evidence_by_dimension: dict[str, DemographicEvidence]
    estimated_unique_users: float | None = None
    status: str = "multiple_marginal_estimates_no_joint_model"

def combine_demographic_evidence(evidence: list[DemographicEvidence]) -> dict[str, ProductAssessment]:
    """Group evidence, preserving each marginal estimate without averaging.

    Reject duplicate product/dimension evidence rather than silently
    selecting one. Different years/geographies are retained with metadata.
    """
    grouped: dict[str, dict[str, DemographicEvidence]] = {}
    for item in evidence:
        dims = grouped.setdefault(item.product, {})
        if item.dimension in dims:
            raise ValueError(f"Duplicate evidence for {item.product}/{item.dimension}")
        dims[item.dimension] = item
    return {product: ProductAssessment(product, dict(dims)) for product, dims in grouped.items()}

def compare_dimensions(assessment: ProductAssessment) -> dict[str, float]:
    """Comparable prevalence diagnostics; not an ensemble estimate."""
    return {dimension: e.estimated_users / e.population_covered
            for dimension, e in assessment.evidence_by_dimension.items()}

def attach_joint_estimate(assessment: ProductAssessment, *,
                          estimated_unique_users: float,
                          validated_joint_source: str) -> ProductAssessment:
    """Only a separately documented validated joint estimate can populate total."""
    if not validated_joint_source.strip():
        raise ValueError("Validated joint source is required")
    covered = {e.population_covered for e in assessment.evidence_by_dimension.values()}
    if len(covered) != 1:
        raise ValueError("Marginal populations differ; align geography and population first")
    if not 0 <= estimated_unique_users <= next(iter(covered)):
        raise ValueError("Joint estimate out of bounds")
    return ProductAssessment(assessment.product, assessment.evidence_by_dimension,
                             estimated_unique_users, "joint_estimate:" + validated_joint_source)

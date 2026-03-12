"""
Service-Based and Product-Based Company Probability Calculator
Calculates placement probability for service and product-based companies
based on student skills and performance metrics.
"""

import pandas as pd


class ServiceProductProbability:
    """Calculate probability for service-based and product-based companies"""

    def __init__(self):
        """Initialize the calculator"""
        self.alpha = 0.6  # Blending factor (ML dominates)

    def calculate_service_score(self, dsa_score, aptitude_score, cs_fundamentals_score, project_score):
        """
        Calculate service-based company score
        Service Companies Weight Formula:
        Service_Score = 0.35 * aptitude_score +
                       0.35 * dsa_score +
                       0.15 * cs_fundamentals_score +
                       0.15 * project_score
        """
        service_score = (
            0.35 * aptitude_score +
            0.35 * dsa_score +
            0.15 * cs_fundamentals_score +
            0.15 * project_score
        )

        # Normalize to 0-1
        s_service = service_score / 100
        return s_service

    def calculate_product_score(self, dsa_score, project_score, cs_fundamentals_score, aptitude_score):
        """
        Calculate product-based company score
        Product Companies Weight Formula:
        Product_Score = 0.45 * dsa_score +
                       0.30 * project_score +
                       0.15 * cs_fundamentals_score +
                       0.10 * aptitude_score
        """
        product_score = (
            0.45 * dsa_score +
            0.30 * project_score +
            0.15 * cs_fundamentals_score +
            0.10 * aptitude_score
        )

        # Normalize to 0-1
        s_product = product_score / 100
        return s_product

    def calculate_final_probabilities(self, p_base, s_service, s_product):
        """
        Calculate final probabilities by blending ML model with logic-based weights
        Final_Probability = α * P_base + (1 - α) * S_company_type
        """
        p_service = (self.alpha * p_base) + ((1 - self.alpha) * s_service)
        p_product = (self.alpha * p_base) + ((1 - self.alpha) * s_product)

        # Convert to percentage and cap between 0-100
        p_service_pct = max(0, min(100, p_service * 100))
        p_product_pct = max(0, min(100, p_product * 100))

        return p_service_pct, p_product_pct

    def get_company_type_probability(self, ml_placement_prob, student_scores):
        """
        Main method to calculate service and product company probabilities

        Args:
            ml_placement_prob: Probability from ML model (0-1)
            student_scores: Dict with keys - dsa_score, project_score, cs_fundamentals_score, aptitude_score

        Returns:
            Dict with service_prob and product_prob
        """
        # Calculate weighted scores based on company type
        s_service = self.calculate_service_score(
            student_scores.get('dsa_score', 50),
            student_scores.get('aptitude_score', 50),
            student_scores.get('cs_fundamentals_score', 50),
            student_scores.get('project_score', 50)
        )

        s_product = self.calculate_product_score(
            student_scores.get('dsa_score', 50),
            student_scores.get('project_score', 50),
            student_scores.get('cs_fundamentals_score', 50),
            student_scores.get('aptitude_score', 50)
        )

        # Calculate final probabilities
        service_prob, product_prob = self.calculate_final_probabilities(
            ml_placement_prob,
            s_service,
            s_product
        )

        return {
            'service_probability': service_prob,
            'product_probability': product_prob,
            'service_score': s_service,
            'product_score': s_product
        }

    def print_analysis(self, student_scores, probabilities):
        """Print detailed analysis of service vs product company suitability"""
        print("\n" + "="*60)
        print("🔍 SERVICE vs PRODUCT COMPANY ANALYSIS")
        print("="*60)

        print("\n📊 Score Breakdown:")
        print(f"   DSA Score: {student_scores.get('dsa_score', 0):.2f}")
        print(f"   Project Score: {student_scores.get('project_score', 0):.2f}")
        print(f"   CS Fundamentals: {student_scores.get('cs_fundamentals_score', 0):.2f}")
        print(f"   Aptitude Score: {student_scores.get('aptitude_score', 0):.2f}")

        print("\n📈 Weighted Scores:")
        print(f"   Service Score: {probabilities['service_score']:.4f}")
        print(f"   Product Score: {probabilities['product_score']:.4f}")

        print("\n🎯 Final Placement Probability:")
        print(f"   Service-Based Companies: {probabilities['service_probability']:.2f}%")
        print(f"   Product-Based Companies: {probabilities['product_probability']:.2f}%")

        # Provide explanation
        if probabilities['product_probability'] > probabilities['service_probability']:
            diff = probabilities['product_probability'] - probabilities['service_probability']
            print(f"\n💡 Insight: You are {diff:.2f}% better suited for product-based companies")
            print("   Reason: Your DSA and project skills are strong, which product companies value more.")
        else:
            diff = probabilities['service_probability'] - probabilities['product_probability']
            print(f"\n💡 Insight: You are {diff:.2f}% better suited for service-based companies")
            print("   Reason: Your aptitude and basic DSA skills make service companies a good fit.")

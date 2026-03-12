"""
Update script to add placement probabilities to student_profiles_100.csv
Fetches data from student_profiles_100 and updates it with probability columns
"""

import pandas as pd
import os
import sys
import io

# Set UTF-8 encoding for console output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from modules.service_product_probability import ServiceProductProbability
from modules.company_wise_probability import CompanyWiseProbability


def update_student_profiles():
    """Update student profiles with placement probabilities"""

    # File paths
    student_csv = os.path.join(os.path.dirname(__file__), 'data/student_profiles_100.csv')

    print("\n" + "="*60)
    print("📊 UPDATING STUDENT PROFILES WITH PROBABILITIES")
    print("="*60)

    # Read student profiles
    print("\n📖 Reading student profiles...")
    try:
        df = pd.read_csv(student_csv)
        print(f"✅ Loaded {len(df)} student profiles")
    except Exception as e:
        print(f"❌ Error reading student profiles: {e}")
        return False

    # Initialize probability calculators
    sp_calc = ServiceProductProbability()
    company_calc = CompanyWiseProbability()

    # Add new columns if they don't exist
    new_columns = [
        'overall_placement_probability',
        'service_company_probability',
        'product_company_probability'
    ]

    for col in new_columns:
        if col not in df.columns:
            df[col] = 0.0

    # Get unique companies from company profiles
    unique_companies = company_calc.company_df['company_name'].unique()

    # Add company-wise columns for top companies
    top_companies = company_calc.company_df.nlargest(15, 'hiring_intensity')['company_name'].tolist()

    for company in top_companies:
        col_name = f"{company}_probability"
        if col_name not in df.columns:
            df[col_name] = 0.0

    # Process each student
    processed_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        student_id = row['student_id']

        # Check if required scores exist
        required_cols = ['dsa_score', 'project_score', 'cs_fundamentals_score', 'aptitude_score']

        # Check if any value is missing (NaN or empty)
        has_missing = False
        for col in required_cols:
            if col not in row.index or pd.isna(row[col]):
                has_missing = True
                break

        if has_missing:
            skipped_count += 1
            continue

        try:
            # Prepare student scores
            student_scores = {
                'dsa_score': float(row['dsa_score']),
                'project_score': float(row['project_score']),
                'cs_fundamentals_score': float(row['cs_fundamentals_score']),
                'aptitude_score': float(row['aptitude_score'])
            }

            # Use a default ML placement probability (0.65 = 65%)
            # In real scenario, this would come from ML model
            ml_placement_prob = 0.65

            # Calculate service/product probabilities
            sp_result = sp_calc.get_company_type_probability(ml_placement_prob, student_scores)

            service_prob = sp_result['service_probability']
            product_prob = sp_result['product_probability']

            # Store probabilities
            df.at[idx, 'overall_placement_probability'] = ml_placement_prob * 100
            df.at[idx, 'service_company_probability'] = service_prob
            df.at[idx, 'product_company_probability'] = product_prob

            # Calculate company-wise probabilities
            company_probs = company_calc.calculate_all_companies(service_prob, product_prob)

            # Store top company probabilities
            for company in top_companies:
                if company in company_probs:
                    col_name = f"{company}_probability"
                    df.at[idx, col_name] = company_probs[company]

            processed_count += 1

            if (processed_count + skipped_count) % 10 == 0:
                print(f"   Processed: {processed_count + skipped_count}/{len(df)}", end='\r')

        except Exception as e:
            print(f"❌ Error processing student {student_id}: {e}")
            skipped_count += 1

    print(f"\n✅ Processed: {processed_count} students")
    print(f"⏭️  Skipped (missing scores): {skipped_count} students")

    # Save updated dataframe
    try:
        print("\n💾 Saving updated profiles...")
        df.to_csv(student_csv, index=False)
        print(f"✅ Successfully updated: {student_csv}")
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False


if __name__ == "__main__":
    try:
        success = update_student_profiles()
        if success:
            print("\n" + "="*60)
            print("🎉 UPDATE COMPLETED SUCCESSFULLY!")
            print("="*60)
        else:
            print("\n❌ Update failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

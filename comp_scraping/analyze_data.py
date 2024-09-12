import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import locale

# Set locale to Portuguese (Brazil) for currency formatting
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def load_data(file_path):
    return pd.read_csv(file_path)

def clean_data(df):
    df['Total Compensation'] = df['Total Compensation'].str.replace('R$', '').str.replace(',', '').astype(float)
    df['Total Compensation'] = df['Total Compensation'] / 12
    df['Years of Experience'] = df['Years of Experience'].str.extract('(\d+)').astype(float)
    df['Years at Company'] = df['Years at Company'].str.extract('(\d+)').astype(float)
    return df

def format_currency(value):
    # Round to 2 decimal places before formatting
    return locale.currency(round(value, 2), grouping=True, symbol='R$')

def categorize_experience(years):
    if years <= 3:
        return '0-3 years'
    elif years <= 7:
        return '4-7 years'
    elif years <= 12:
        return '8-12 years'
    else:
        return '13+ years'

def categorize_companies(df):
    # Calculate median compensation for each company
    company_median = df.groupby('Company')['Total Compensation'].median().sort_values(ascending=False)

    # Calculate percentile thresholds
    threshold_90 = company_median.quantile(0.90)
    threshold_70 = company_median.quantile(0.70)

    # Categorize companies into tiers
    tier_3 = company_median[company_median > threshold_90].index.tolist()
    tier_2 = company_median[(company_median > threshold_70) & (company_median <= threshold_90)].index.tolist()
    tier_1 = company_median[company_median <= threshold_70].index.tolist()

    return {
        'Tier 3 (Global)': tier_3,
        'Tier 2 (All Local)': tier_2,
        'Tier 1 (Local)': tier_1
    }

def analyze_data(df):
    results = {}

    # Experience group analysis
    df['Experience Group'] = df['Years of Experience'].apply(categorize_experience)
    exp_group_stats = df.groupby('Experience Group')['Total Compensation'].agg(['count', 'mean', 'median',
                                                                                lambda x: x.quantile(0.75),
                                                                                lambda x: x.quantile(0.90)])
    exp_group_stats.columns = ['count', 'mean', 'p50', 'p75', 'p90']
    exp_group_stats = exp_group_stats.sort_values('mean', ascending=False)

    results['Compensation Stats by Experience Group'] = exp_group_stats.apply(lambda x: x.apply(format_currency) if x.name != 'count' else x).to_dict()

    # Overall compensation stats
    overall_stats = df['Total Compensation'].agg(['count', 'mean', 'median',
                                                  lambda x: x.quantile(0.75),
                                                  lambda x: x.quantile(0.90)])
    overall_stats.index = ['count', 'mean', 'p50', 'p75', 'p90']

    formatted_stats = overall_stats.copy()
    for stat in ['mean', 'p50', 'p75', 'p90']:
        formatted_stats[stat] = format_currency(formatted_stats[stat])
    formatted_stats['count'] = int(formatted_stats['count'])

    results['Overall Compensation Stats'] = formatted_stats.to_dict()

    # Top paying companies by experience group
    top_companies_by_group = {}
    for group in ['0-3 years', '4-7 years', '8-12 years', '13+ years']:
        group_df = df[df['Experience Group'] == group]
        company_avg = group_df.groupby('Company').agg({
            'Total Compensation': 'mean',
            'Company': 'count'
        }).rename(columns={'Company': 'Count'}).sort_values('Total Compensation', ascending=False)

        top_companies = company_avg[company_avg['Count'] >= 3].head(10)
        top_companies['Total Compensation'] = top_companies['Total Compensation'].apply(format_currency)
        top_companies_by_group[group] = top_companies

    results['Top Paying Companies by Experience Group'] = top_companies_by_group

    # Experience vs Compensation correlation
    exp_corr = df['Years of Experience'].corr(df['Total Compensation'])
    results['Correlation (Years of Experience vs Total Compensation)'] = f"{exp_corr:.2f}"

    # Company tenure vs Compensation correlation
    tenure_corr = df['Years at Company'].corr(df['Total Compensation'])
    results['Correlation (Years at Company vs Total Compensation)'] = f"{tenure_corr:.2f}"

    # Add company tiers analysis
    company_tiers = categorize_companies(df)
    results['Company Tiers'] = company_tiers

    # Add tier information to the dataframe
    df['Company Tier'] = df['Company'].map({company: tier
                                            for tier, companies in company_tiers.items()
                                            for company in companies})

    # Calculate average compensation by tier
    tier_stats = df.groupby('Company Tier')['Total Compensation'].agg(['mean', 'median'])
    tier_stats = tier_stats.sort_values('mean', ascending=False)
    tier_stats = tier_stats.map(format_currency)
    results['Compensation Stats by Company Tier'] = tier_stats.to_dict()

    # Convert results to a more notebook-friendly format
    formatted_results = {
        'Compensation Stats by Experience Group': results['Compensation Stats by Experience Group'],
        'Overall Compensation Stats': results['Overall Compensation Stats'],
        'Top Paying Companies by Experience Group': {group: companies.to_dict() for group, companies in results['Top Paying Companies by Experience Group'].items()},
        'Correlation (Years of Experience vs Total Compensation)': results['Correlation (Years of Experience vs Total Compensation)'],
        'Correlation (Years at Company vs Total Compensation)': results['Correlation (Years at Company vs Total Compensation)'],
        'Company Tiers': results['Company Tiers'],  # Add this line
        'Compensation Stats by Company Tier': results['Compensation Stats by Company Tier'],
    }

    return formatted_results

if __name__ == "__main__":
    file_path = 'data/brazil_software_engineer_salaries_2024-09-11-00-27-27.csv'
    df = load_data(file_path)
    df = clean_data(df)
    results = analyze_data(df)
    print("Analysis complete. Plots are available in the 'plots' key of the results dictionary.")

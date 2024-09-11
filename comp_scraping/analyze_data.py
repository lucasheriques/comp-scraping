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
    df['Years of Experience'] = df['Years of Experience'].str.extract('(\d+)').astype(float)
    df['Years at Company'] = df['Years at Company'].str.extract('(\d+)').astype(float)
    return df

def format_currency(value):
    return locale.currency(value, grouping=True, symbol='R$')

def categorize_experience(years):
    if years <= 3:
        return '0-3 years'
    elif years <= 7:
        return '4-7 years'
    elif years <= 12:
        return '8-12 years'
    else:
        return '13+ years'

def analyze_data(df):
    results = {}

    # Experience group analysis
    df['Experience Group'] = df['Years of Experience'].apply(categorize_experience)
    exp_group_avg = df.groupby('Experience Group')['Total Compensation'].mean().sort_values(ascending=False)
    results['Average Compensation by Experience Group'] = exp_group_avg.apply(format_currency).to_frame('Average Compensation')

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

    # Highest average salary overall
    results['Highest Average Salary Overall'] = format_currency(df['Total Compensation'].mean())

    # Experience vs Compensation correlation
    exp_corr = df['Years of Experience'].corr(df['Total Compensation'])
    results['Correlation (Years of Experience vs Total Compensation)'] = f"{exp_corr:.2f}"

    # Company tenure vs Compensation correlation
    tenure_corr = df['Years at Company'].corr(df['Total Compensation'])
    results['Correlation (Years at Company vs Total Compensation)'] = f"{tenure_corr:.2f}"

    # Convert results to a more notebook-friendly format
    formatted_results = {
        'Average Compensation by Experience Group': results['Average Compensation by Experience Group'].to_dict()['Average Compensation'],
        'Top Paying Companies by Experience Group': {group: companies.to_dict() for group, companies in results['Top Paying Companies by Experience Group'].items()},
        'Highest Average Salary Overall': results['Highest Average Salary Overall'],
        'Correlation (Years of Experience vs Total Compensation)': results['Correlation (Years of Experience vs Total Compensation)'],
        'Correlation (Years at Company vs Total Compensation)': results['Correlation (Years at Company vs Total Compensation)'],
    }

    return formatted_results

if __name__ == "__main__":
    file_path = 'data/brazil_software_engineer_salaries_2024-09-11-00-27-27.csv'
    df = load_data(file_path)
    df = clean_data(df)
    results = analyze_data(df)
    print("Analysis complete. Plots are available in the 'plots' key of the results dictionary.")

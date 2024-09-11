import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file_path):
    return pd.read_csv(file_path)

def clean_data(df):
    df['Total Compensation'] = df['Total Compensation'].str.replace('R$', '').str.replace(',', '').astype(float)
    return df

def categorize_companies(df):
    thresholds = df['Total Compensation'].quantile([0.33, 0.67])

    def assign_tier(comp):
        if comp <= thresholds.iloc[0]:
            return 'Tier 1'
        elif comp <= thresholds.iloc[1]:
            return 'Tier 2'
        else:
            return 'Tier 3'

    df['Tier'] = df['Total Compensation'].apply(assign_tier)
    return df

def analyze_data(df):
    print("Summary Statistics by Tier:")
    print(df.groupby('Tier').agg({
        'Company': 'count',
        'Total Compensation': ['mean', 'median', 'min', 'max']
    }))

    print("\nTop 10 Companies by Average Compensation:")
    top_companies = df.groupby('Company')['Total Compensation'].mean().sort_values(ascending=False).head(10)
    print(top_companies)

    print("\nTop 10 Companies by Average Compensation (with at least 5 data points):")
    company_counts = df['Company'].value_counts()
    companies_with_5_plus = company_counts[company_counts >= 5].index
    top_companies_5_plus = df[df['Company'].isin(companies_with_5_plus)].groupby('Company')['Total Compensation'].mean().sort_values(ascending=False).head(10)
    print(top_companies_5_plus)

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Tier', y='Total Compensation', data=df)
    plt.title('Total Compensation by Tier')
    plt.ylabel('Total Compensation (R$)')
    plt.savefig('compensation_by_tier.png')
    plt.close()

    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='Total Compensation', hue='Tier', multiple='stack')
    plt.title('Distribution of Total Compensation by Tier')
    plt.xlabel('Total Compensation (R$)')
    plt.ylabel('Frequency')
    plt.savefig('compensation_distribution.png')
    plt.close()

    # Location analysis
    location_avg_comp = df.groupby('Location')['Total Compensation'].mean().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    location_avg_comp.plot(kind='bar')
    plt.title('Top 10 Locations by Average Compensation')
    plt.xlabel('Location')
    plt.ylabel('Average Total Compensation (R$)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('top_locations.png')
    plt.close()

    # New plot for top companies with 5+ data points
    plt.figure(figsize=(12, 6))
    top_companies_5_plus.plot(kind='bar')
    plt.title('Top 10 Companies by Average Compensation (5+ data points)')
    plt.xlabel('Company')
    plt.ylabel('Average Total Compensation (R$)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('top_companies_5_plus.png')
    plt.close()

if __name__ == "__main__":
    file_path = 'brazil_software_engineer_salaries.csv'
    df = load_data(file_path)
    df = clean_data(df)
    df = categorize_companies(df)
    analyze_data(df)
    print("Analysis complete. Check the generated PNG files for visualizations.")

import requests
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt

def get_indicator(country_code, country_name, indicator_code, indicator_name):
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json"
    response = requests.get(url)
    data = response.json()
    records = data[1]

    clean_data = []
    for record in records:
        clean_data.append({
            'Country': country_name,
            'Indicator': indicator_name,
            'Year': record['date'],
            'Value': record['value']
        })

    df = pd.DataFrame(clean_data)
    df['Year'] = df['Year'].astype(int)
    df = df.sort_values(by='Year')
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df

# Countries and indicators we're tracking
countries = {
    "US": "United States", "GB": "United Kingdom", "DE": "Germany", "FR": "France",
    "JP": "Japan", "CA": "Canada", "AU": "Australia", "KR": "South Korea",
    "IN": "India", "CN": "China", "BR": "Brazil", "RU": "Russia", "ZA": "South Africa",
    "ID": "Indonesia", "MX": "Mexico", "TR": "Turkey", "SA": "Saudi Arabia",
    "NG": "Nigeria", "EG": "Egypt", "PK": "Pakistan", "BD": "Bangladesh",
    "VN": "Vietnam", "KE": "Kenya", "AR": "Argentina", "TH": "Thailand"
}

indicators = {
    'NY.GDP.MKTP.KD.ZG': 'GDP Growth (%)',
    'FP.CPI.TOTL.ZG': 'Inflation (%)',
    'SL.UEM.TOTL.ZS': 'Unemployment (%)',
}

healthcare_indicators = {
    "SH.XPD.CHEX.GD.ZS" : "Health Expenditure (% of GDP)",
    "SH.XPD.OOPC.CH.ZS" : "Out-of-Pocket Health Expenditure (% of Health Spending)",
    "SH.XPD.GHED.GD.ZS" : "Government Health Expenditure (% of GDP)",
    "SH.XPD.PVTD.CH.ZS" : "Private Health Expenditure (% of Health Spending)"
}

if __name__ == "__main__":
    # All your data-fetching loops go here.
    
    # Fetch everything: 4 countries x 3 indicators = 12 datasets
    all_data = []
    for country_code, country_name in countries.items():
        for indicator_code, indicator_name in indicators.items():
            df = get_indicator(country_code, country_name, indicator_code, indicator_name)
            all_data.append(df)

    combined = pd.concat(all_data)
    combined = combined.reset_index(drop=True)

    # Fetching the healthcare indicators for the same countries
    healthcare_data = []
    for country_code, country_name in countries.items():
        for indicator_code, indicator_name in healthcare_indicators.items():
            df = get_indicator(country_code, country_name, indicator_code, indicator_name)
            healthcare_data.append(df)

    healthcare_combined = pd.concat(healthcare_data)
    healthcare_combined = healthcare_combined.reset_index(drop=True)

    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 12), sharex=True)

    for i, indicator_name in enumerate(indicators.values()):
        subset = combined[combined['Indicator'] == indicator_name]
        for country_name, group in subset.groupby('Country'):
            group = group.sort_values(by='Year')
            smoothed = group['Value'].rolling(window=5).mean()
            axes[i].plot(group['Year'], smoothed, label=country_name)
        axes[i].set_title(indicator_name)
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()

    axes[1].set_yscale('symlog', linthresh=0.1)   # apply log scale to the second subplot (Inflation)
    axes[1].set_ylabel('Inflation (%) - Log Scale')

    axes[-1].set_xlabel('Year')
    fig.suptitle('Economic Indicators Comparison (5-Year Rolling Average)', fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.savefig('economic_indicators_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()

    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 10))
    axes = axes.flatten()

    for i, indicator_name in enumerate(healthcare_indicators.values()):
        subset = healthcare_combined[healthcare_combined['Indicator'] == indicator_name]
        for country_name, group in subset.groupby('Country'):
            group = group.sort_values(by='Year')
            smoothed = group['Value'].rolling(window=5).mean()
            axes[i].plot(group['Year'], smoothed, label=country_name)
        axes[i].set_title(indicator_name)
        axes[i].grid(True, alpha=0.3)
        axes[i].legend()

    fig.suptitle('Healthcare Financing Comparison: India, USA, China, Brazil', fontsize=14)
    fig.text(0.5, 0.02, "Year", ha="center")
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig('healthcare_financing_comparison.png', dpi=150, bbox_inches='tight')
    plt.show()

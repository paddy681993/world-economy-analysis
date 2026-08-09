import requests
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt


def get_gdp_growth_data(country_code, country_name):
    """
    Fetches GDP growth data for a given country using the World Bank API.

    Args:
        country_code (str): The ISO 3166-1 alpha-3 country code.
        country_name (str): The name of the country.
    """
    # World Bank API endpoint for GDP growth data
    url = f"https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.KD.ZG?format=json"
    response = requests.get(url)
    data = response.json()
    records = data[1]  # The second element contains the actual data

    clean_data = []
    for record in records:
        year = record['date']
        gdp_growth = record['value']
        country = country_name
        clean_data.append({'Year': year, 'GDP Growth (%)': gdp_growth, 'Country': country})

    # Create a DataFrame from the cleaned data
    df = pd.DataFrame(clean_data)
    df = df.sort_values("Year")
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df

# Now call it for multiple countries
india = get_gdp_growth_data('IND', 'India')
usa = get_gdp_growth_data('USA', 'United States')
china = get_gdp_growth_data('CHN', 'China')
brazil = get_gdp_growth_data('BRA', 'Brazil')

# Combine into one big table
all_countries = pd.concat([india, usa, china, brazil], ignore_index=True)
all_countries = all_countries.reset_index(drop=True)

print(all_countries)
all_countries["Year"] = all_countries["Year"].astype(int)

plt.figure(figsize=(12, 6))

for country_name, group in all_countries.groupby('Country'):
    group = group.sort_values("Year")
    smoothed = group["GDP Growth (%)"].rolling(window=5).mean()
    plt.plot(group["Year"], smoothed, label=country_name)

plt.xlabel('Year')
plt.ylabel('GDP Growth (%)')
plt.title('GDP Growth Comparison: India, USA, China, Brazil')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from economic_analysis import get_indicator, countries, indicators, healthcare_indicators

st.title("Global Economic and Healthcare Indicators Dashboard")
st.write("Comparing India, USA, China, and Brazil across economic and healthcare indicators.")

@st.cache_data
def load_all_data():
    all_indicators = {**indicators, **healthcare_indicators}
    all_data = []
    for country_code, country_name in countries.items():
        for indicator_code, indicator_name in all_indicators.items():
            df = get_indicator(country_code, country_name, indicator_code, indicator_name)
            all_data.append(df)
    combined = pd.concat(all_data)
    combined = combined.reset_index(drop=True)
    return combined

data = load_all_data()

# Dropdown to select which indicator to view
selected_indicator = st.selectbox("Choose an Indicator:", data['Indicator'].unique())

smooth = st.checkbox("Apply 5-Year Rolling Average (smooths noisy trends)")
log_scale = st.checkbox("Use symlog scale (for indicators with extreme outliers, e.g., Inflation)")

st.write(f"Displaying data for: {selected_indicator}")

selected_data = data[data['Indicator'] == selected_indicator]

fig, ax = plt.subplots(figsize=(10, 5))
for country_name, group in selected_data.groupby('Country'):
    group = group.sort_values(by='Year')
    values = group['Value']
    if smooth:
        values = values.rolling(window=5).mean()
    ax.plot(group['Year'], values, label=country_name)

if log_scale:
    ax.set_yscale('symlog', linthresh=1)

ax.set_title(selected_indicator)
ax.set_xlabel("Year")
ax.set_ylabel(selected_indicator)
ax.legend()
ax.grid(True, alpha=0.3)

st.pyplot(fig)
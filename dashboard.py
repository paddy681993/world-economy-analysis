import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from economic_analysis import get_indicator, countries, indicators, healthcare_indicators

st.title("Global Economic and Healthcare Indicators Dashboard")
st.write("Explore economic and healthcare indicators across 25 countries.")

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

with st.spinner("Loading data from World Bank API 25 countries... this may take a minute on first load."):
    data = load_all_data()

tab1, tab2, tab3 = st.tabs(["Country Profile", "Rankings", "Comparison"])

# Tab 1: Country Profile
with tab1:
    selected_country = st.selectbox("Select a Country:", sorted(countries.values()))

    all_indicator_names = list(indicators.values()) + list(healthcare_indicators.values())
    selected_profile_indicator = st.selectbox("Select an Indicator:", all_indicator_names, key="profile_indicator")

    col1, col2 = st.columns(2)
    with col1:
        smooth = st.checkbox("Apply 5-Year Rolling Average.")

    with col2:
        log_scale = st.checkbox("Use symlog scale (for indicators with extreme outliers)")

    country_data = data[data['Country'] == selected_country]
    indicator_data = country_data[country_data['Indicator'] == selected_profile_indicator]
    indicator_data = indicator_data.sort_values(by='Year')

    values = indicator_data['Value']
    if smooth:
        values = values.rolling(window=5).mean()

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(indicator_data['Year'], values)

    if log_scale:
        ax.set_yscale('symlog', linthresh=1)

    ax.set_title(f"{selected_profile_indicator} - {selected_country}")
    ax.set_xlabel("Year")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

# Tab 2: Rankings
with tab2:
    all_indicator_names = list(indicators.values()) + list(healthcare_indicators.values())
    selected_indicator = st.selectbox("Select an Indicator:", all_indicator_names)

    indicator_data = data[data["Indicator"] == selected_indicator]

    year_counts = indicator_data.groupby('Year')['Country'].count()
    max_coverage = year_counts.max()
    best_years = year_counts[year_counts == max_coverage].index
    latest_year = best_years.max() # if multiple years tie for best coverage, pick the most recent
     
    latest_data = indicator_data[indicator_data['Year'] == latest_year]
    latest_data = latest_data.sort_values(by='Value', ascending=False)

    st.write(f"Showing {selected_indicator} for {latest_year} ({len(latest_data)} countries with available data)")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 5")
        st.dataframe(latest_data.head(5)[['Country', 'Value']])

    with col2:
        st.subheader("Bottom 5")
        st.dataframe(latest_data.tail(5)[['Country', 'Value']])

with tab3:
    all_indicator_names = list(indicators.values()) + list(healthcare_indicators.values())
    comparison_indicator = st.selectbox("Select an indicator:", all_indicator_names, key="comparison_indicator")

    selection_mode = st.radio("Choose countries by:", ["Custom Selection", "Preset group"])

    g7 = ["United States", "United Kingdom", "Germany", "France", "Japan", "Canada"]
    brics = ["Brazil", "Russia", "India", "China", "South Africa"]

    if selection_mode == "Custom Selection":
        col_a, col_b = st.columns(2)
        with col_a:
            group_a = st.multiselect(
                "Group A:",
                sorted(countries.values()),
                default=["India", "China"],
                key="group_a"
            )

        with col_b:
            group_b = st.multiselect(
                "Group B:",
                sorted(countries.values()),
                default=["United States"],
                key="group_b"
            )

        selected_countries = group_a + group_b
        country_group_map = {c: "Group A" for c in group_a}
        country_group_map.update({c: "Group B" for c in group_b})
    else:
        group = st.radio("Choose a group:", ["G7", "BRICS"])
        selected_countries = g7 if group == 'G7' else brics
        country_group_map = {c: group for c in selected_countries}
        st.write(f"Comparing: {', '.join(selected_countries)}")

    if len(selected_countries) == 0:
        st.warning("Please select at least one country.")
    else:
        smooth_compare = st.checkbox("Apply 5-year rolling average", key="smooth_compare")
        log_compare = st.checkbox("Use symbol scale", key="log_compare")

        comparison_data = data[
            (data["Indicator"] == comparison_indicator) &
            (data["Country"].isin(selected_countries))
        ]

        fig, ax = plt.subplots(figsize=(10, 5))
        for country_name, group_df in comparison_data.groupby("Country"):
            group_df = group_df.sort_values("Year")
            values = group_df["Value"]
            if smooth_compare:
                values = values.rolling(window=5).mean()

            linestyle = "-" if country_group_map.get(country_name) == "Group A" else "--"
            ax.plot(group_df["Year"], values, label=country_name, linestyle=linestyle)

        if log_compare:
            ax.set_yscale("symlog", linthresh=1)

        ax.set_title(comparison_indicator)
        ax.set_xlabel("Year")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
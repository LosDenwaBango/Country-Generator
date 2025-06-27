import streamlit as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import requests
import numpy as np
import io
import datetime
import pycountry
import pycountry_convert
import country_converter as coco

# Build a list of all countries with their alpha_2 codes and continent
continent_map = {
    'AF': 'Africa',
    'AS': 'Asia',
    'EU': 'Europe',
    'NA': 'North America',
    'OC': 'Oceania',
    'SA': 'South America',
    'AN': 'Antarctica'
}

# List of UN member states' alpha_2 codes (plus AQ for Antarctica)
UN_MEMBER_ALPHA2 = set([
    'AF', 'AL', 'DZ', 'AD', 'AO', 'AG', 'AR', 'AM', 'AU', 'AT', 'AZ',
    'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BT', 'BO', 'BA', 'BW',
    'BR', 'BN', 'BG', 'BF', 'BI', 'CV', 'KH', 'CM', 'CA', 'CF', 'TD', 'CL',
    'CN', 'CO', 'KM', 'CD', 'CG', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'DK',
    'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'SZ', 'ET', 'FJ',
    'FI', 'FR', 'GA', 'GM', 'GE', 'DE', 'GH', 'GR', 'GD', 'GT', 'GN', 'GW',
    'GY', 'HT', 'HN', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IL', 'IT',
    'JM', 'JP', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV',
    'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MG', 'MW', 'MY', 'MV', 'ML',
    'MT', 'MH', 'MR', 'MU', 'MX', 'FM', 'MD', 'MC', 'MN', 'ME', 'MA', 'MZ',
    'MM', 'NA', 'NR', 'NP', 'NL', 'NZ', 'NI', 'NE', 'NG', 'MK', 'NO', 'OM',
    'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PL', 'PT', 'QA', 'RO',
    'RU', 'RW', 'KN', 'LC', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC',
    'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'SS', 'ES', 'LK', 'SD', 'SR',
    'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TO', 'TT', 'TN',
    'TR', 'TM', 'UG', 'UA', 'AE', 'GB', 'US', 'UY', 'UZ', 'VU', 'VA', 'VE',
    'VN', 'YE', 'ZM', 'ZW', 'AQ'  # Antarctica
])

COUNTRY_LIST = []
def get_continent(alpha_2):
    special_cases = {
        'AQ': 'Antarctica',
        'TL': 'Asia',         # Timor-Leste is in Asia
        'VA': 'Europe',       # Vatican City is in Europe
        'TR': 'Europe',       # Turkey in Europe for this app
    }
    if alpha_2 in special_cases:
        return special_cases[alpha_2]
    try:
        continent_code = pycountry_convert.country_alpha2_to_continent_code(alpha_2)
        return continent_map.get(continent_code, 'Unknown')
    except Exception:
        return 'Unknown'
for country in list(pycountry.countries):
    if hasattr(country, 'alpha_2') and country.alpha_2 in UN_MEMBER_ALPHA2:
        short_name = coco.convert(names=country.alpha_2, to='name_short')
        COUNTRY_LIST.append({
            "name": short_name,
            "alpha_2": country.alpha_2,
            "continent": get_continent(country.alpha_2)
        })

def get_countries_by_continent():
    from collections import defaultdict
    countries = defaultdict(list)
    for c in COUNTRY_LIST:
        countries[c["continent"]].append(c)
    for cont in countries:
        countries[cont] = sorted(countries[cont], key=lambda x: x["name"])
    return countries

# --- Sample data ---
# countries = [
#     {"code": "GBR", "age": 0, "type": "lived"},
#     {"code": "ESP", "age": 10, "type": "visited"},
#     {"code": "FRA", "age": 13, "type": "visited"},
#     {"code": "GRC", "age": 16, "type": "visited"},
#     {"code": "CHE", "age": 18, "type": "visited"},
#     {"code": "JPN", "age": 25, "type": "lived"},
# ]

# Date of birth inputs (no calculations)
dob_col1, dob_col2 = st.columns(2)
with dob_col1:
    st.number_input("Month of birth", min_value=1, max_value=12, value=1, key="dob_month")
with dob_col2:
    st.number_input("Year of birth", min_value=1900, max_value=2100, value=1990, key="dob_year")

st.markdown("### Countries visited")
countries_by_cont = get_countries_by_continent()

# --- Multi-select for country selection, then month/year inputs below ---
country_options = [f"{c['name']} ({c['alpha_2']})" for c in COUNTRY_LIST]
selected_labels = st.multiselect("Select countries you have visited", country_options)

if selected_labels:
    st.markdown('### Enter month and year you first visited each country:')
    for label in selected_labels:
        c = next(c for c in COUNTRY_LIST if f"{c['name']} ({c['alpha_2']})" == label)
        code = c["alpha_2"]
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(f"Month you first visited {c['name']}", min_value=1, max_value=12, value=1, key=f"visit_month_{code}")
        with col2:
            st.number_input(f"Year you first visited {c['name']}", min_value=1900, max_value=2100, value=1990, key=f"visit_year_{code}")

if st.button("Generate!"):
    # All calculations and list building happen here
    dob_month = st.session_state.get("dob_month", 1)
    dob_year = st.session_state.get("dob_year", 1990)
    visited = []
    visit_ages = {}
    for label in selected_labels:
        c = next(c for c in COUNTRY_LIST if f"{c['name']} ({c['alpha_2']})" == label)
        code = c["alpha_2"]
        visit_month = st.session_state.get(f"visit_month_{code}", 1)
        visit_year = st.session_state.get(f"visit_year_{code}", 1990)
        age = (visit_year - dob_year) + (visit_month - dob_month) / 12
        visited.append({'country': c, 'age': age, 'visit_month': visit_month, 'visit_year': visit_year})
        visit_ages[code] = age

    if not visited:
        st.warning("Please select at least one country and enter the age you first visited.")
    else:
        visited_sorted = sorted(visited, key=lambda x: x['age'], reverse=True)
        country_names = [c['country']['name'] for c in visited_sorted]
        ages = [c['age'] for c in visited_sorted]
        codes = [c['country']['alpha_2'] for c in visited_sorted]
        flag_dir = "Flags"
        os.makedirs(flag_dir, exist_ok=True)
        def download_flag(code, flag_path):
            url = f"https://flagcdn.com/w40/{code.lower()}.png"
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                with open(flag_path, "wb") as f:
                    f.write(r.content)
                return True
            except Exception as e:
                st.warning(f"Could not download flag for {code}: {e}")
                return False
        for code in codes:
            flag_path = os.path.join(flag_dir, f"{code}.png")
            if not os.path.exists(flag_path):
                download_flag(code, flag_path)
        if not ages:
            st.error("No ages found for plotting. Please check your selections.")
        else:
            # Calculate current age from dob_month and dob_year
            today = datetime.date.today()
            birth_date = datetime.date(dob_year, dob_month, 1)
            # Calculate age in years, accounting for month
            current_age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, 1))
            bar_height = 1.0  # Bars and flags touch each other
            fig_height = max(4, len(visited_sorted) * bar_height)
            fig, ax = plt.subplots(figsize=(16, fig_height))  # Keep bar/flag size consistent

            age_min = 0  # Start at 0
            age_max = current_age + 5
            for age in range(age_min, age_max + 1):
                ax.axvline(age, color='gray', linestyle=':', linewidth=0.5, zorder=0)

            for i in range(0, len(visited_sorted), 5):
                ax.axhspan(i - 0.5, min(i + 4.5, len(visited_sorted) - 0.5), color='lightgray', alpha=0.15, zorder=0)

            cmap = plt.get_cmap('tab20')
            colors = list(cmap(np.linspace(0, 1, len(visited_sorted))))

            for i, c in enumerate(visited_sorted):
                code = c['country']['alpha_2']
                country_name = c['country']['name']
                color = colors[i % len(colors)]
                # Extend the bar from visit age up to current age
                ax.barh(i, current_age - c['age'], left=c['age'], color=color, alpha=0.7, height=bar_height, zorder=2)
                flag_path = os.path.join(flag_dir, f"{code}.png")
                if os.path.exists(flag_path):
                    try:
                        img = mpimg.imread(flag_path)
                        img_height, img_width = img.shape[:2]
                        aspect = img_width / img_height
                        flag_height = bar_height
                        flag_width = flag_height * aspect * 2.5  # Make flags longer horizontally
                        # Shift flag 50% to the right: left edge at current center (age)
                        ax.imshow(
                            img,
                            extent=(c['age'], c['age']+flag_width, i-flag_height/2, i+flag_height/2),
                            aspect='auto',
                            zorder=10,
                            origin='lower'
                        )
                    except Exception as e:
                        st.warning(f"Could not load flag image for {code}: {e}")
            # Restore y-tick labels to show country and age on the left
            ax.set_yticks(range(len(visited_sorted)))
            ax.set_yticklabels([f"{c['country']['name']} ({c['age']})" for c in visited_sorted])
            # Adjust y-limits to ensure the top flag is not cut off
            ax.set_ylim(-0.5, len(visited_sorted)-0.5)

            ax.set_xlabel("Your age", fontsize=14)
            ax.set_xlim(age_min, current_age + 1)  # Chart ends at current age
            ax.set_title("Countries visited by age", fontsize=18)
            ax.invert_yaxis()  # Oldest visit at the bottom
            ax.grid(axis='x', linestyle=':', linewidth=0.5, alpha=0.7, zorder=1)

            st.pyplot(fig)
            n_countries = len(visited_sorted)
            age_now = max(ages)
            percent = (n_countries / age_now) * 100 if age_now > 0 else 0
            st.info(f"You have visited {n_countries} countries. This is {percent:.1f}% of your age.")
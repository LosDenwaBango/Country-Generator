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

# Hardcoded small list of countries for troubleshooting
COUNTRY_LIST = [
    {"name": "United Kingdom", "alpha_2": "GB", "continent": "Europe"},
    {"name": "Spain", "alpha_2": "ES", "continent": "Europe"},
    {"name": "Japan", "alpha_2": "JP", "continent": "Asia"},
    {"name": "South Africa", "alpha_2": "ZA", "continent": "Africa"},
    {"name": "United States", "alpha_2": "US", "continent": "North America"},
    {"name": "Australia", "alpha_2": "AU", "continent": "Oceania"},
]

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

dob_col1, dob_col2 = st.columns(2)
with dob_col1:
    dob_month = st.number_input("Month of birth", min_value=1, max_value=12, value=1)
with dob_col2:
    dob_year = st.number_input("Year of birth", min_value=1900, max_value=2100, value=1990)

st.markdown("### Countries visited")
countries_by_cont = get_countries_by_continent()
visited = []
visit_ages = {}

for cont, clist in countries_by_cont.items():
    with st.expander(cont):
        for c in clist:
            code = c["alpha_2"]
            label = f"{c['name']} ({code})"
            if st.checkbox(label, key=code):
                age = st.number_input(f"Age when you first visited {c['name']}", min_value=0, max_value=120, value=20, key=f"age_{code}")
                visited.append((c, age))
                visit_ages[code] = age

if st.button("Generate!"):
    if not visited:
        st.warning("Please select at least one country and enter the age you first visited.")
    else:
        visited_sorted = sorted(visited, key=lambda x: x[1], reverse=True)
        country_names = [c["name"] for c, _ in visited_sorted]
        ages = [age for _, age in visited_sorted]
        codes = [c["alpha_2"] for c, _ in visited_sorted]
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

            for i, (c, age) in enumerate(visited_sorted):
                code = c["alpha_2"]
                country_name = c["name"]
                color = colors[i % len(colors)]
                # Extend the bar from visit age up to current age
                ax.barh(i, current_age - age, left=age, color=color, alpha=0.7, height=bar_height, zorder=2)
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
                            extent=(age, age+flag_width, i-flag_height/2, i+flag_height/2),
                            aspect='auto',
                            zorder=10,
                            origin='lower'
                        )
                    except Exception as e:
                        st.warning(f"Could not load flag image for {code}: {e}")
            # Restore y-tick labels to show country and age on the left
            ax.set_yticks(range(len(visited_sorted)))
            ax.set_yticklabels([f"{c['name']} ({age})" for c, age in visited_sorted])
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
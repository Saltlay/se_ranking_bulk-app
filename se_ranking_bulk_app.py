import os
import streamlit as st
import requests
import pandas as pd

# Streamlit app setup
st.set_page_config(page_title="SE Ranking Bulk Domain Analyzer", layout="centered")
st.title("🔍 SE Ranking Bulk Domain Analyzer")

# Securely load API key from environment or Streamlit Secrets
api_key = os.getenv("SERANKING_API_KEY") or st.secrets.get("SERANKING_API_KEY")

if not api_key:
    st.warning("⚠️ API key not found. Please set SERANKING_API_KEY in your environment or Streamlit Secrets.")
else:
    st.info("✅ API key loaded securely")

# Input domains
domains_input = st.text_area(
    "Enter domains (one per line)",
    placeholder="example.com\nanotherdomain.com\nthirdsite.org"
)

# Choose metrics
selected_params = st.multiselect(
    "Select metrics to fetch",
    ["domain_trust", "backlinks", "keywords_count", "organic_traffic", "visibility"],
    default=["domain_trust", "organic_traffic"]
)

# Fetch Data Button
if st.button("Fetch Data"):
    if not api_key:
        st.error("Missing API key. Please set it before fetching data.")
    elif not domains_input.strip():
        st.error("Please enter at least one domain.")
    else:
        domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
        results = []

        progress = st.progress(0)
        status_area = st.empty()

        for i, domain in enumerate(domains):
            # SE Ranking API endpoint
            url = f"https://api.seranking.com/v3/domain/overview?domain={domain}"
            headers = {"Authorization": f"Bearer {api_key}"}

            try:
                response = requests.get(url, headers=headers)
                status_area.text(f"Fetching data for {domain}... ({i+1}/{len(domains)})")

                # Handle non-JSON responses
                try:
                    data = response.json()
                except ValueError:
                    results.append({"domain": domain, "error": f"Invalid response: {response.text[:100]}"})
                    continue

                if response.status_code != 200:
                    results.append({"domain": domain, "error": data.get("message", response.text)})
                    continue

                if "data" in data and data["data"]:
                    info = data["data"][0]
                    record = {"domain": domain}
                    for param in selected_params:
                        record[param] = info.get(param, "N/A")
                    results.append(record)
                else:
                    results.append({"domain": domain, "error": data.get("message", "No data returned")})

            except Exception as e:
                results.append({"domain": domain, "error": str(e)})

            progress.progress((i + 1) / len(domains))

        # Create DataFrame
        df = pd.DataFrame(results)
        st.success("✅ Data fetched successfully!")
        st.dataframe(df)

        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="se_ranking_bulk_results.csv",
            mime="text/csv"
        )

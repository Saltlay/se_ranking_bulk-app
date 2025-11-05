import os
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="SE Ranking Bulk Domain Analyzer", layout="centered")
st.title("🔍 SE Ranking Bulk Domain Analyzer")

# Securely load API key (works for local + Streamlit Cloud)
api_key = os.getenv("SERANKING_API_KEY") or st.secrets.get("SERANKING_API_KEY")

if not api_key:
    st.warning("⚠️ API key not found. Please set SERANKING_API_KEY in your environment or Streamlit Secrets.")
else:
    st.info("✅ API key loaded securely")

domains_input = st.text_area(
    "Enter domains (one per line)",
    placeholder="example.com\nanotherdomain.com\nthirdsite.org"
)

selected_params = st.multiselect(
    "Select metrics to fetch",
    ["visibility", "organic_traffic", "keywords_count", "backlinks", "domain_trust"],
    default=["visibility", "organic_traffic"]
)

if st.button("Fetch Data"):
    if not api_key:
        st.error("Missing API key. Please set it before fetching data.")
    elif not domains_input.strip():
        st.error("Please enter at least one domain.")
    else:
        domains = [d.strip() for d in domains_input.split("\n") if d.strip()]
        results = []

        progress = st.progress(0)
        for i, domain in enumerate(domains):
            url = f"https://api.seranking.com/v3/sites?domain={domain}"
            headers = {"Authorization": f"Bearer {api_key}"}

            try:
                response = requests.get(url, headers=headers)
                data = response.json()

                if data.get("data"):
                    info = data["data"][0]
                    record = {"domain": domain}
                    for param in selected_params:
                        record[param] = info.get(param, "N/A")
                    results.append(record)
                else:
                    results.append({"domain": domain, "error": data.get("message", "No data")})

            except Exception as e:
                results.append({"domain": domain, "error": str(e)})

            progress.progress((i + 1) / len(domains))

        df = pd.DataFrame(results)
        st.success("✅ Data fetched successfully!")
        st.dataframe(df)

        csv = df.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name="se_ranking_data.csv", mime="text/csv")

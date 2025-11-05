for i, domain in enumerate(domains):
    url = f"https://api.seranking.com/v3/domain/overview?domain={domain}"
    headers = {"Authorization": f"Token {api_key}"}  # changed from Bearer to Token

    try:
        response = requests.get(url, headers=headers)
        status_area.text(f"Fetching data for {domain}... ({i+1}/{len(domains)})")

        try:
            data = response.json()
        except ValueError:
            results.append({"domain": domain, "error": f"Invalid response: {response.text[:100]}"})
            continue

        if response.status_code != 200:
            results.append({"domain": domain, "error": data.get('message', response.text)})
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

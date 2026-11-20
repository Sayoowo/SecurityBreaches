# AI Agent Security Incidents: Streamlit Portfolio App

A multi-page Streamlit app that doubles as my data visualization portfolio and a small analytics product. It explores real-world security incidents and vulnerabilities involving AI agents from late 2024 to 2026: which attack types are most common, how volume and severity have changed over time, and where incidents are reported.

**Live app:** _add your Streamlit Cloud URL here after deploying_

## Author

**Sayo Owolabi**, Computer Science student
[LinkedIn](https://www.linkedin.com/in/sayo-owolabi)

## App navigation

| Page | What it shows |
|---|---|
| **Home** (`app.py`) | Project overview and a guide to the pages |
| **Bio** | Professional summary, highlights, and my visualization philosophy |
| **EDA Gallery** | Five charts (bar, line with a 2028 projection toggle, histogram with an attack-type filter, treemap, bubble map), each with the question it explores, a "How to read this chart" guide, observations, and its data source |
| **Dashboard** | Sidebar filters (date range, severity, attack type), four KPIs, two linked charts, insight bullets, an ethics note, a data source badge, and a "last updated" timestamp |
| **Future Work** | Five concrete next steps and a reflection on how the app changed from the paper prototype |

## Dataset

- **Name:** AI Agent Security and Real-World Incidents (2024–26)
- **Source:** [Kaggle: muhammadahmerkhan](https://www.kaggle.com/datasets/muhammadahmerkhan/ai-agent-security-and-real-world-incidents-2024-26)
- **Records:** 395 rows in the full file; **217** used in the app
- **Files used:** `dataset/ai_agent_incidents_full.csv`, `dataset/taxonomy_attack_types.csv`

### Preprocessing

- Kept only rows where `kind` is `incident` or `vulnerability` (217 of 395). Policy, research, and report entries were excluded because they are not attacks.
- Converted `date` and `month` to real dates; unreadable dates become blank instead of stopping the app.
- Split multi-label fields (`type`, `region`) on `;` so a record tagged with two attack types counts toward each one.
- Replaced attack-type and region codes with readable names using the taxonomy file.
- Mapped severity labels to scores (low = 1 to critical = 4) for the histogram.
- Filled months with no records with zero for the line chart, started the trend at January 2025, and left October 2026 (a partial month) out of the projection fit.
- No rows were imputed or invented.

### Ethics note

This dataset describes real incidents involving real organizations and, in some cases, the people affected by them. Because it is built from publicly reported sources, it may over-represent English-language and US coverage and under-count incidents that were never disclosed. Severity ratings were assigned by the dataset author. The charts show patterns in what was reported. They should not be used to judge specific companies or to draw conclusions about attacks that were not reported.

## Requirements

All Python packages and their versions are listed in [`requirements.txt`](requirements.txt).

## How to run locally

```bash
git clone https://github.com/Sayoowo/SecurityBreaches.git
cd SecurityBreaches
pip install -r requirements.txt
streamlit run app.py
```

## Screenshots

_Optional: add 1–3 screenshots of the app pages here._

## AI assistance

I used Claude (Anthropic) as a tutor to plan charts, explain code, and debug errors while building this app.

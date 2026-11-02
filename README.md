# Healthcare Recruitment Funnel Analytics

Analyses a sourcing → screening → interview → submission → placement funnel for nursing and
allied-health roles and produces a self-contained `report.html`.

**Data:** 1,200 SYNTHETIC records (`generate_data.py`) using assumed conversion rates per channel.
Findings illustrate the method; they are not real market results.

## Outputs
- Funnel with step conversion
- Channel yield (sourced→placed, submit→place)
- Median time-to-fill and placement rate by specialty
- Monthly sourcing trend

## Run
```
pip install -r requirements.txt
mkdir -p data && python generate_data.py
python analysis.py        # writes report.html
```
## Next steps
Swap in real ATS exports, add Power BI/Streamlit front-end, add public US healthcare labor data for demand context.

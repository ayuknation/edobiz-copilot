# EdoBiz Copilot 🇳🇬

### Talk your business. EdoBiz handles the numbers.

EdoBiz Copilot is a prototype AI-powered business assistant designed to help Nigerian small businesses record transactions, understand their finances, and make better business decisions using natural language.

## MVP Demo

The first prototype lets a business owner:

- Record sales and expenses using plain English or Nigerian Pidgin
- Convert simple natural-language entries into structured transactions
- View revenue, expenses and estimated net contribution
- Ask basic business questions in English or Pidgin
- Review recent transactions and a simple performance chart

### Example

> “I sell 5 bags of rice today for 425k and spend 9k for transport.”

EdoBiz extracts the transaction and updates the dashboard.

Then ask:

> “How my business dey do this month?”

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The prototype currently uses a lightweight local parser so it can be demonstrated without exposing an API key. A production version can connect the natural-language layer to a secure AI service, add speech-to-text, authentication, persistent cloud storage, and consent-based financial integrations.

## Project Status

**Prototype / In Development 🚧**

## Important

This prototype is for demonstration and product validation. Its calculations are estimates based on user-entered records. It does not make loan, credit, or banking decisions.

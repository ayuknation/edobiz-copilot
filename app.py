import re
from datetime import date
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='EdoBiz Copilot', page_icon='🇳🇬', layout='wide')

DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / 'transactions.csv'

COLUMNS = ['date','type','description','category','quantity','amount']

DEMO_DATA = [
    [str(date.today()), 'Sale', 'Rice - 5 bags', 'Sales', 5, 425000],
    [str(date.today()), 'Expense', 'Transport', 'Transport', 1, 9000],
    [str(date.today()), 'Sale', 'Drinks - 10 cartons', 'Sales', 10, 180000],
    [str(date.today()), 'Expense', 'Fuel', 'Operations', 1, 25000],
    [str(date.today()), 'Sale', 'Cement - 20 bags', 'Sales', 20, 220000],
    [str(date.today()), 'Expense', 'Loading', 'Operations', 1, 8000],
]

def load_data():
    if DATA_FILE.exists():
        try:
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                return df[COLUMNS]
        except Exception:
            pass
    return pd.DataFrame(DEMO_DATA, columns=COLUMNS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def money(n):
    return f"₦{n:,.0f}"

def parse_amount(text):
    text = text.lower().replace(',', '').replace('₦', '').replace('ngn', '')
    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(million|m|thousand|k)?', text)
    if not matches:
        return None
    value, suffix = matches[-1]
    value = float(value)
    if suffix in ('million','m'):
        value *= 1_000_000
    elif suffix in ('thousand','k'):
        value *= 1_000
    return int(value)

def parse_transaction(text):
    t = text.lower().strip()
    sale_words = ['sell','sold','sale','sales','make','made','receive','received','customer pay','customer paid']
    expense_words = ['spend','spent','expense','buy','bought','purchase','transport','fuel','loading','rent','paid']
    is_expense = any(w in t for w in expense_words) and not any(w in t for w in ['sell','sold','sales'])
    is_sale = any(w in t for w in sale_words)
    amount = parse_amount(t)
    if amount is None:
        return None
    tx_type = 'Expense' if is_expense and not is_sale else 'Sale'
    qty = 1
    q = re.search(r'(\d+)\s+(bags?|cartons?|pieces?|pcs?|units?|items?)', t)
    if q:
        qty = int(q.group(1))
    category = 'Sales' if tx_type == 'Sale' else 'Operations'
    for cat, words in {
        'Transport':['transport','delivery'], 'Fuel':['fuel','petrol','diesel'],
        'Inventory':['buy','bought','purchase','stock'], 'Rent':['rent'],
        'Loading':['loading','loader']}.items():
        if any(w in t for w in words): category = cat
    desc = text.strip().capitalize()
    return {'date': str(date.today()), 'type': tx_type, 'description': desc,
            'category': category, 'quantity': qty, 'amount': amount}

def copilot_response(question, df):
    q = question.lower()
    sales = df.loc[df.type == 'Sale', 'amount'].sum()
    expenses = df.loc[df.type == 'Expense', 'amount'].sum()
    profit = sales - expenses
    if any(x in q for x in ['how my business','how is my business','business dey do','performance','performing']):
        return f"Your business dey move well. Sales this period na {money(sales)}, expenses na {money(expenses)}, so your estimated net contribution na {money(profit)}. Keep an eye on operating costs, especially transport and fuel."
    if any(x in q for x in ['profit','make','gain']):
        return f"Based on the records, your estimated net contribution na {money(profit)} ({money(sales)} sales minus {money(expenses)} expenses)."
    if any(x in q for x in ['sales','sell','revenue']):
        return f"Your recorded sales na {money(sales)}. You get {len(df[df.type == 'Sale'])} sale entries in the current records."
    if any(x in q for x in ['expense','spend','spent','cost']):
        return f"Your recorded expenses na {money(expenses)}. The biggest expense category is {df[df.type == 'Expense'].groupby('category').amount.sum().sort_values(ascending=False).index[0] if not df[df.type == 'Expense'].empty else 'not available'}."
    if any(x in q for x in ['product','which one','best']):
        products = df[df.type == 'Sale'].copy()
        if products.empty: return 'No sales records yet.'
        return f"Your strongest recorded sales entry is: {products.sort_values('amount', ascending=False).iloc[0]['description']} at {money(products.amount.max())}."
    if any(x in q for x in ['restock','afford','cash']):
        return f"Your current recorded net contribution is {money(profit)}. Before restocking, check your actual cash balance, upcoming bills and supplier prices. EdoBiz no be loan approval system; this is a planning estimate."
    return "I understand English and Nigerian Pidgin. Try: 'How my business dey do this month?', 'How much profit I make?', or 'Which product dey sell pass?'"

# Sidebar
with st.sidebar:
    st.title('🇳🇬 EdoBiz Copilot')
    st.caption('Talk your business. EdoBiz handles the numbers.')
    st.divider()
    if st.button('Reset to Demo Data', use_container_width=True):
        df = pd.DataFrame(DEMO_DATA, columns=COLUMNS)
        save_data(df)
        st.rerun()
    st.info('Prototype only. Financial figures are estimates from entered records and are not loan or credit decisions.')

if 'df' not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df.copy()

st.title('EdoBiz Copilot')
st.write('### Your small-business intelligence assistant')
st.caption('Record transactions in plain English or Nigerian Pidgin, then ask questions about your business.')

sales = df.loc[df.type == 'Sale', 'amount'].sum()
expenses = df.loc[df.type == 'Expense', 'amount'].sum()
profit = sales - expenses

c1,c2,c3,c4 = st.columns(4)
c1.metric('Revenue', money(sales))
c2.metric('Expenses', money(expenses))
c3.metric('Estimated Net', money(profit))
c4.metric('Transactions', len(df))

st.divider()

left, right = st.columns([1,1])
with left:
    st.subheader('💬 Talk to EdoBiz')
    example = st.selectbox('Try an example', [
        'How my business dey do this month?',
        'How much profit I make?',
        'Which product dey sell pass?',
        'How much I spend?'
    ])
    question = st.text_input('Ask in English or Pidgin', value=example)
    if st.button('Ask EdoBiz', type='primary', use_container_width=True):
        st.success(copilot_response(question, df))

with right:
    st.subheader('➕ Record a transaction')
    text = st.text_area('Type naturally', placeholder='e.g. I sell 5 bags of rice today for 425k and spend 9k for transport.')
    if st.button('Understand & Record', use_container_width=True):
        parsed = parse_transaction(text)
        if parsed:
            df = pd.concat([df, pd.DataFrame([parsed])], ignore_index=True)
            st.session_state.df = df
            save_data(df)
            st.success(f"Recorded {parsed['type'].lower()}: {money(parsed['amount'])} — {parsed['description']}")
            st.rerun()
        else:
            st.error('I could not confidently detect an amount. Try something like: "I sell 3 bags for 255k".')

st.divider()
st.subheader('📊 Business Overview')

chart_df = df.copy()
chart_df['date'] = pd.to_datetime(chart_df['date'])
daily = chart_df.groupby(['date','type'])['amount'].sum().unstack(fill_value=0)
st.line_chart(daily)

st.subheader('Recent Transactions')
st.dataframe(df.sort_values('date', ascending=False), use_container_width=True, hide_index=True)

st.caption('EdoBiz Copilot — Prototype / In Development 🚧')

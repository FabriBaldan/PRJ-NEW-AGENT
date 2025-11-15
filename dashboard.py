"""
Dashboard Interattiva per Consulente di Investimento AI
Interfaccia Streamlit per visualizzare raccomandazioni di investimento
"""
import streamlit as st
import os
from datetime import datetime
from investment_agent import create_investment_agent
from langchain_core.messages import HumanMessage, AIMessage
import re

# Configurazione della pagina
st.set_page_config(
    page_title="💼 Consulente di Investimento AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card h4 {
        color: #1f77b4;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-card p {
        color: #666;
        font-size: 1rem;
    }
    .recommendation-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
        color: #155724;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .stock-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def parse_recommendations(content: str) -> dict:
    """Estrae informazioni strutturate dalle raccomandazioni."""
    result = {
        "market_overview": {},
        "allocation": {},
        "sectors": [],
        "stocks": [],
        "recommendations": [],
        "conclusion": ""
    }
    
    # Estrai panoramica mercato
    sp500_match = re.search(r'S&P 500.*?([+-]?\d+\.\d+)%', content)
    nasdaq_match = re.search(r'NASDAQ.*?([+-]?\d+\.\d+)%', content)
    vix_match = re.search(r'VIX.*?(\d+\.\d+)', content)
    sentiment_match = re.search(r'Sentiment.*?:\s*(\w+)', content, re.IGNORECASE)
    
    if sp500_match:
        result["market_overview"]["sp500"] = float(sp500_match.group(1))
    if nasdaq_match:
        result["market_overview"]["nasdaq"] = float(nasdaq_match.group(1))
    if vix_match:
        result["market_overview"]["vix"] = float(vix_match.group(1))
    if sentiment_match:
        result["market_overview"]["sentiment"] = sentiment_match.group(1)
    
    # Estrai allocazione
    azioni_match = re.search(r'Azioni.*?€([\d,]+)', content)
    bonds_match = re.search(r'Obbligazioni.*?€([\d,]+)', content)
    liquidita_match = re.search(r'Liquidità.*?€([\d,]+)', content)
    
    if azioni_match:
        result["allocation"]["stocks"] = float(azioni_match.group(1).replace(',', ''))
    if bonds_match:
        result["allocation"]["bonds"] = float(bonds_match.group(1).replace(',', ''))
    if liquidita_match:
        result["allocation"]["cash"] = float(liquidita_match.group(1).replace(',', ''))
    
    # Estrai stocks con prezzi
    stock_pattern = r'([A-Z]{2,5}).*?€([\d.]+).*?\(([+-]?\d+\.\d+)%\)'
    for match in re.finditer(stock_pattern, content):
        result["stocks"].append({
            "ticker": match.group(1),
            "price": float(match.group(2)),
            "change": float(match.group(3))
        })
    
    # Estrai raccomandazioni per ticker con importi
    rec_pattern = r'([A-Z]{2,5}):\s*€([\d,]+)'
    for match in re.finditer(rec_pattern, content):
        result["recommendations"].append({
            "ticker": match.group(1),
            "amount": float(match.group(2).replace(',', ''))
        })
    
    # Estrai conclusione
    conclusion_match = re.search(r'### Conclusione\s+(.*?)(?=###|$)', content, re.DOTALL)
    if conclusion_match:
        result["conclusion"] = conclusion_match.group(1).strip()
    
    return result


def run_investment_analysis(amount: float, risk_profile: str):
    """Esegue l'analisi di investimento."""
    agent_app = create_investment_agent()
    
    initial_message = HumanMessage(
        content=f"""Sono un investitore con €{amount:,.2f} da investire.
        
Il mio profilo di rischio è: {risk_profile}

Per favore:
1. Analizza la situazione attuale del mercato usando get_market_overview
2. Calcola l'allocazione ottimale del portafoglio con calculate_portfolio_allocation
3. Analizza i settori più promettenti con analyze_sector_performance
4. Ottieni quotazioni di titoli specifici usando get_stock_quote per i top picks
5. Fornisci raccomandazioni dettagliate con razionale

Sii specifico e fornisci ticker, percentuali di allocazione, e giustificazioni."""
    )
    
    initial_state = {
        "messages": [initial_message],
        "investment_amount": amount,
        "risk_profile": risk_profile,
        "recommendations": [],
        "market_data": {},
        "rationale": "",
        "next_action": "start"
    }
    
    config = {"configurable": {"thread_id": f"investment_session_{datetime.now().timestamp()}"}}
    
    with st.spinner("🤖 L'agente AI sta analizzando i mercati..."):
        final_state = agent_app.invoke(initial_state, config)
    
    # Estrai la risposta finale
    for msg in final_state["messages"]:
        if isinstance(msg, AIMessage) and not (hasattr(msg, "tool_calls") and msg.tool_calls):
            return msg.content, final_state
    
    return None, final_state


# Header
st.markdown('<h1 class="main-header">💼 Consulente di Investimento AI</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar per input
with st.sidebar:
    st.header("⚙️ Configurazione")
    
    st.markdown("### 💰 Capitale da Investire")
    amount = st.number_input(
        "Importo (€)",
        min_value=1000.0,
        max_value=1000000.0,
        value=10000.0,
        step=1000.0,
        help="Inserisci l'importo che desideri investire"
    )
    
    st.markdown("### 📊 Profilo di Rischio")
    risk_profile = st.selectbox(
        "Seleziona il tuo profilo",
        options=["conservative", "moderate", "aggressive"],
        index=1,
        help="""
        - **Conservative**: Basso rischio, focus su stabilità
        - **Moderate**: Bilanciato tra crescita e stabilità
        - **Aggressive**: Alto rischio, focus su crescita
        """
    )
    
    # Descrizione profili
    risk_descriptions = {
        "conservative": "🛡️ **Conservativo**: Priorità alla sicurezza del capitale con investimenti a basso rischio (30% azioni, 50% obbligazioni)",
        "moderate": "⚖️ **Moderato**: Bilanciamento tra crescita e stabilità (60% azioni, 30% obbligazioni)",
        "aggressive": "🚀 **Aggressivo**: Focus sulla crescita con maggiore tolleranza al rischio (80% azioni, 10% obbligazioni)"
    }
    
    st.info(risk_descriptions[risk_profile])
    
    st.markdown("---")
    
    analyze_button = st.button("🔍 Analizza Investimenti", type="primary", use_container_width=True)

# Area principale
if analyze_button:
    # Esegui l'analisi
    content, state = run_investment_analysis(amount, risk_profile)
    
    if content:
        # Salva in session state
        st.session_state.analysis_result = content
        st.session_state.parsed_data = parse_recommendations(content)
        st.session_state.amount = amount
        st.session_state.risk_profile = risk_profile

# Mostra i risultati se disponibili
if "analysis_result" in st.session_state:
    parsed = st.session_state.parsed_data
    
    # Sezione 1: Panoramica Mercato
    st.header("📈 Panoramica Mercato")
    
    if parsed["market_overview"]:
        cols = st.columns(4)
        
        if "sp500" in parsed["market_overview"]:
            with cols[0]:
                delta_color = "normal" if parsed["market_overview"]["sp500"] >= 0 else "inverse"
                st.metric(
                    "S&P 500",
                    f"{parsed['market_overview']['sp500']:+.2f}%",
                    delta=f"{parsed['market_overview']['sp500']:.2f}%",
                    delta_color=delta_color
                )
        
        if "nasdaq" in parsed["market_overview"]:
            with cols[1]:
                delta_color = "normal" if parsed["market_overview"]["nasdaq"] >= 0 else "inverse"
                st.metric(
                    "NASDAQ",
                    f"{parsed['market_overview']['nasdaq']:+.2f}%",
                    delta=f"{parsed['market_overview']['nasdaq']:.2f}%",
                    delta_color=delta_color
                )
        
        if "vix" in parsed["market_overview"]:
            with cols[2]:
                st.metric(
                    "VIX (Volatilità)",
                    f"{parsed['market_overview']['vix']:.2f}",
                    help="Indice di volatilità del mercato"
                )
        
        if "sentiment" in parsed["market_overview"]:
            with cols[3]:
                sentiment_emoji = {"bullish": "📈", "neutral": "➡️", "bearish": "📉"}
                sentiment = parsed["market_overview"]["sentiment"].lower()
                emoji = sentiment_emoji.get(sentiment, "➡️")
                st.metric(
                    "Sentiment",
                    f"{emoji} {sentiment.capitalize()}"
                )
    
    st.markdown("---")
    
    # Sezione 2: Allocazione Portafoglio
    st.header("💼 Allocazione Portafoglio Ottimale")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if parsed["allocation"]:
            st.markdown("### 📊 Distribuzione Asset")
            
            total = sum(parsed["allocation"].values())
            for asset, value in parsed["allocation"].items():
                percentage = (value / total * 100) if total > 0 else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{asset.capitalize()}</h4>
                    <h2>€{value:,.2f}</h2>
                    <p style="color: #666;">{percentage:.1f}% del portafoglio</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if parsed["allocation"]:
            st.markdown("### 📈 Visualizzazione")
            
            # Crea dati per il grafico
            import pandas as pd
            df = pd.DataFrame([
                {"Asset": k.capitalize(), "Importo": v}
                for k, v in parsed["allocation"].items()
            ])
            
            st.bar_chart(df.set_index("Asset"))
    
    st.markdown("---")
    
    # Sezione 3: Raccomandazioni Specifiche
    st.header("🎯 Raccomandazioni di Investimento")
    
    if parsed["recommendations"]:
        # Raggruppa per settore (semplificato)
        tech_stocks = ["AAPL", "MSFT", "NVDA", "GOOGL"]
        health_stocks = ["JNJ", "UNH", "PFE", "ABBV"]
        
        tech_recs = [r for r in parsed["recommendations"] if r["ticker"] in tech_stocks]
        health_recs = [r for r in parsed["recommendations"] if r["ticker"] in health_stocks]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if tech_recs:
                st.markdown("### 💻 Settore Tecnologia")
                for rec in tech_recs:
                    stock_info = next((s for s in parsed["stocks"] if s["ticker"] == rec["ticker"]), None)
                    change_emoji = "📈" if stock_info and stock_info["change"] > 0 else "📉"
                    
                    st.markdown(f"""
                    <div class="stock-card">
                        <h3>{change_emoji} {rec['ticker']}</h3>
                        <h2>€{rec['amount']:,.2f}</h2>
                        {f"<p>Prezzo: €{stock_info['price']:.2f} ({stock_info['change']:+.2f}%)</p>" if stock_info else ""}
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            if health_recs:
                st.markdown("### 🏥 Settore Healthcare")
                for rec in health_recs:
                    stock_info = next((s for s in parsed["stocks"] if s["ticker"] == rec["ticker"]), None)
                    change_emoji = "📈" if stock_info and stock_info["change"] > 0 else "📉"
                    
                    st.markdown(f"""
                    <div class="stock-card">
                        <h3>{change_emoji} {rec['ticker']}</h3>
                        <h2>€{rec['amount']:,.2f}</h2>
                        {f"<p>Prezzo: €{stock_info['price']:.2f} ({stock_info['change']:+.2f}%)</p>" if stock_info else ""}
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sezione 4: Analisi Completa
    st.header("📋 Analisi Completa e Giustificazioni")
    
    with st.expander("📄 Visualizza Report Completo", expanded=False):
        st.markdown(st.session_state.analysis_result)
    
    # Sezione 5: Conclusioni
    if parsed["conclusion"]:
        st.header("💡 Conclusioni")
        st.markdown(f"""
        <div class="success-box">
            {parsed['conclusion']}
        </div>
        """, unsafe_allow_html=True)
    
    # Sezione 6: DAG dell'Agente
    st.header("🔀 Architettura dell'Agente AI")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Grafo del Workflow")
        if os.path.exists("investment_agent_dag.png"):
            st.image("investment_agent_dag.png", use_container_width=True)
        else:
            st.info("Esegui `python visualize_investment_dag.py` per generare il DAG")
    
    with col2:
        st.markdown("### 🔄 Flusso di Esecuzione")
        st.markdown("""
        **1. START → Agent**
        - Riceve input utente (importo, profilo rischio)
        
        **2. Agent → Tools** 
        - Decide autonomamente quali dati servono
        - Analizza mercati e settori
        
        **3. Tools → Agent (Loop)**
        - Esegue chiamate MCP Alpha Vantage:
          - `get_market_overview()`
          - `calculate_portfolio_allocation()`
          - `analyze_sector_performance()`
          - `get_stock_quote()`
        
        **4. Agent → Finalize**
        - Quando ha dati sufficienti
        - Genera raccomandazioni strutturate
        
        **5. Finalize → END**
        - Output: portfolio + rationale dettagliato
        """)
    
    # Footer con info
    st.markdown("---")
    st.markdown(f"""
    <div class="warning-box">
        ⚠️ <strong>Disclaimer</strong>: Queste raccomandazioni sono generate da un'AI e utilizzano dati simulati. 
        Non costituiscono consulenza finanziaria. Consulta sempre un professionista prima di investire.
    </div>
    """, unsafe_allow_html=True)
    
    # Pulsante per nuova analisi
    if st.button("🔄 Nuova Analisi", use_container_width=True):
        for key in ["analysis_result", "parsed_data"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

else:
    # Schermata iniziale
    st.info("👈 Configura i parametri nella barra laterale e clicca su **Analizza Investimenti** per iniziare")
    
    # Mostra features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI-Powered
        Utilizza LangGraph e GPT-4 
        per analisi intelligenti
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Dati Real-Time
        Analisi di mercato 
        e quotazioni aggiornate
        """)
    
    with col3:
        st.markdown("""
        ### 🎯 Personalizzato
        Raccomandazioni basate 
        sul tuo profilo di rischio
        """)

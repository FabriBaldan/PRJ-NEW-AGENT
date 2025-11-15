"""
Agente di Investimento Intelligente con LangGraph e Alpha Vantage MCP
Suggerisce investimenti basati su dati di mercato in tempo reale
"""
import os
import sys
from typing import TypedDict, Annotated, Sequence
from operator import add

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Carica configurazione
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("Devi impostare OPENAI_API_KEY nel file .env")

# Configura il modello
import httpx
http_client = httpx.Client(verify=False) if os.getenv("SSL_VERIFY", "true").lower() == "false" else None

model = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0.2,  # Leggermente creativo ma preciso
    http_client=http_client,
)


# ------------ Stato dell'Agente ------------

class InvestmentAgentState(TypedDict):
    """Stato dell'agente di investimento."""
    messages: Annotated[Sequence[BaseMessage], add]
    investment_amount: float
    risk_profile: str  # conservative, moderate, aggressive
    recommendations: list
    market_data: dict
    rationale: str
    next_action: str


# ------------ Tools per Alpha Vantage (Placeholder per MCP) ------------

@tool
def get_stock_quote(symbol: str) -> dict:
    """Ottiene la quotazione corrente di un'azione.
    
    Args:
        symbol: Simbolo del titolo (es: AAPL, MSFT, GOOGL)
        
    Returns:
        Dizionario con prezzo, variazione, volume
    """
    # TODO: Integrare con MCP Alpha Vantage
    # Per ora ritorna dati mock
    import random
    base_prices = {
        "AAPL": 180.0,
        "MSFT": 380.0,
        "GOOGL": 140.0,
        "AMZN": 150.0,
        "TSLA": 250.0,
        "NVDA": 500.0,
        "SPY": 450.0,  # S&P 500 ETF
        "QQQ": 380.0,  # NASDAQ ETF
        "VTI": 240.0,  # Total Market ETF
        "BND": 75.0,   # Bond ETF
    }
    
    price = base_prices.get(symbol.upper(), 100.0)
    change_pct = random.uniform(-3.0, 3.0)
    
    return {
        "symbol": symbol.upper(),
        "price": round(price * (1 + change_pct/100), 2),
        "change_percent": round(change_pct, 2),
        "volume": random.randint(1000000, 50000000),
        "market_cap": f"${random.randint(100, 3000)}B"
    }


@tool
def get_market_overview() -> dict:
    """Ottiene una panoramica generale del mercato.
    
    Returns:
        Dati su indici principali, sentiment, volatilità
    """
    # TODO: Integrare con MCP Alpha Vantage
    import random
    
    return {
        "sp500_change": round(random.uniform(-1.5, 1.5), 2),
        "nasdaq_change": round(random.uniform(-2.0, 2.0), 2),
        "dow_change": round(random.uniform(-1.0, 1.0), 2),
        "vix": round(random.uniform(12.0, 25.0), 2),
        "sentiment": random.choice(["bullish", "neutral", "bearish"]),
        "sector_leaders": ["Technology", "Healthcare", "Financials"]
    }


@tool
def analyze_sector_performance(sector: str) -> dict:
    """Analizza la performance di un settore specifico.
    
    Args:
        sector: Nome del settore (Technology, Healthcare, Energy, etc.)
        
    Returns:
        Performance del settore e top titoli
    """
    # TODO: Integrare con MCP Alpha Vantage
    import random
    
    top_stocks = {
        "Technology": ["AAPL", "MSFT", "NVDA", "GOOGL"],
        "Healthcare": ["JNJ", "UNH", "PFE", "ABBV"],
        "Energy": ["XOM", "CVX", "COP", "SLB"],
        "Financials": ["JPM", "BAC", "WFC", "GS"],
        "Consumer": ["AMZN", "TSLA", "NKE", "MCD"]
    }
    
    return {
        "sector": sector,
        "ytd_performance": round(random.uniform(-10.0, 30.0), 2),
        "trend": random.choice(["upward", "stable", "downward"]),
        "top_stocks": top_stocks.get(sector, ["N/A"]),
        "volatility": random.choice(["low", "medium", "high"])
    }


@tool
def calculate_portfolio_allocation(amount: float, risk_profile: str) -> dict:
    """Calcola l'allocazione ottimale del portafoglio in base al profilo di rischio.
    
    Args:
        amount: Importo da investire
        risk_profile: conservative, moderate, aggressive
        
    Returns:
        Allocazione suggerita per asset class
    """
    allocations = {
        "conservative": {
            "stocks": 0.30,
            "bonds": 0.50,
            "cash": 0.15,
            "commodities": 0.05
        },
        "moderate": {
            "stocks": 0.60,
            "bonds": 0.30,
            "cash": 0.05,
            "commodities": 0.05
        },
        "aggressive": {
            "stocks": 0.80,
            "bonds": 0.10,
            "cash": 0.05,
            "commodities": 0.05
        }
    }
    
    allocation = allocations.get(risk_profile.lower(), allocations["moderate"])
    
    return {
        "total_amount": amount,
        "risk_profile": risk_profile,
        "allocation": {
            asset: round(amount * pct, 2) 
            for asset, pct in allocation.items()
        },
        "allocation_percentages": allocation
    }


# Lista dei tools
tools = [
    get_stock_quote,
    get_market_overview,
    analyze_sector_performance,
    calculate_portfolio_allocation
]


# ------------ Nodi del Grafo ------------

def agent_node(state: InvestmentAgentState) -> InvestmentAgentState:
    """Nodo dell'agente: decide quali tools usare per analizzare."""
    messages = state["messages"]
    
    model_with_tools = model.bind_tools(tools)
    response = model_with_tools.invoke(messages)
    
    return {
        **state,
        "messages": [response]
    }


def tool_node(state: InvestmentAgentState) -> InvestmentAgentState:
    """Esegue i tools richiesti dall'agente."""
    tool_executor = ToolNode(tools)
    result = tool_executor.invoke(state)
    return result


def should_continue(state: InvestmentAgentState) -> str:
    """Decide se continuare con tools o finalizzare."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    return "finalize"


def finalize_recommendations(state: InvestmentAgentState) -> InvestmentAgentState:
    """Finalizza le raccomandazioni di investimento."""
    messages = state["messages"]
    
    # Estrai le raccomandazioni dai messaggi
    recommendations = []
    market_data = {}
    
    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            if "recommendation" in msg.content.lower() or "invest" in msg.content.lower():
                recommendations.append(msg.content)
    
    # Genera un rationale finale
    rationale = """
    Analisi completata con successo.
    Le raccomandazioni sono basate su:
    - Analisi di mercato corrente
    - Profilo di rischio specificato
    - Diversificazione ottimale del portafoglio
    """
    
    return {
        **state,
        "recommendations": recommendations,
        "rationale": rationale,
        "next_action": "complete"
    }


# ------------ Costruzione del Grafo ------------

def create_investment_agent():
    """Crea il grafo dell'agente di investimento."""
    workflow = StateGraph(InvestmentAgentState)
    
    # Aggiungi nodi
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("finalize", finalize_recommendations)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Aggiungi edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "finalize": "finalize"
        }
    )
    
    workflow.add_edge("tools", "agent")
    workflow.add_edge("finalize", END)
    
    # Compila
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


# ------------ Funzione Principale ------------

def get_investment_advice(amount: float, risk_profile: str = "moderate"):
    """Ottiene consigli di investimento dall'agente.
    
    Args:
        amount: Importo da investire
        risk_profile: conservative, moderate, aggressive
    """
    agent_app = create_investment_agent()
    
    # Messaggio iniziale
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
    
    print(f"\n{'='*70}")
    print(f"💼 CONSULENTE DI INVESTIMENTO AI")
    print(f"{'='*70}")
    print(f"💰 Capitale disponibile: €{amount:,.2f}")
    print(f"📊 Profilo di rischio: {risk_profile.upper()}")
    print(f"{'='*70}\n")
    print("🔍 Analisi in corso...\n")
    
    config = {"configurable": {"thread_id": "investment_session"}}
    
    try:
        final_state = agent_app.invoke(initial_state, config)
        
        print("\n" + "="*70)
        print("📋 RACCOMANDAZIONI DI INVESTIMENTO")
        print("="*70 + "\n")
        
        # Estrai e stampa la risposta finale
        for msg in final_state["messages"]:
            if isinstance(msg, AIMessage) and not (hasattr(msg, "tool_calls") and msg.tool_calls):
                print(msg.content)
                print()
        
        return final_state
        
    except Exception as e:
        print(f"❌ Errore durante l'analisi: {e}")
        return None


if __name__ == "__main__":
    # Parametri da riga di comando o valori di default
    if len(sys.argv) > 1:
        amount = float(sys.argv[1])
    else:
        amount = 10000.0  # Default: €10,000
    
    if len(sys.argv) > 2:
        risk_profile = sys.argv[2].lower()
    else:
        risk_profile = "moderate"  # Default: moderate
    
    # Valida risk profile
    if risk_profile not in ["conservative", "moderate", "aggressive"]:
        print(f"⚠️  Profilo di rischio '{risk_profile}' non valido.")
        print("   Usa: conservative, moderate, o aggressive")
        sys.exit(1)
    
    # Esegui l'agente
    get_investment_advice(amount, risk_profile)

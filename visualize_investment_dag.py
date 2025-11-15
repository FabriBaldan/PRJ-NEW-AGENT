"""
Visualizza il DAG dell'agente di investimento
"""
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

from investment_agent import create_investment_agent

env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_path)


def create_investment_dag_visual():
    """Crea visualizzazione grafica del DAG."""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Posizioni dei nodi
    positions = {
        'START': (5, 9),
        'agent': (5, 7),
        'tools': (2.5, 5),
        'finalize': (5, 3),
        'END': (5, 1)
    }
    
    # Colori
    colors = {
        'START': '#90EE90',
        'agent': '#87CEEB',
        'tools': '#FFD700',
        'finalize': '#FFA07A',
        'END': '#FF6B6B'
    }
    
    # Disegna nodi
    for node, (x, y) in positions.items():
        if node in ['START', 'END']:
            circle = plt.Circle((x, y), 0.4, color=colors[node], ec='black', linewidth=2, zorder=3)
            ax.add_patch(circle)
        else:
            box = FancyBboxPatch((x-0.8, y-0.35), 1.6, 0.7,
                                boxstyle="round,pad=0.1",
                                facecolor=colors[node],
                                edgecolor='black',
                                linewidth=2, zorder=3)
            ax.add_patch(box)
        
        ax.text(x, y, node, ha='center', va='center',
               fontsize=13, fontweight='bold', zorder=4)
    
    # Arrows
    arrows = [
        ('START', 'agent', 'solid', 'black'),
        ('agent', 'tools', 'dashed', 'blue'),
        ('tools', 'agent', 'solid', 'green'),
        ('agent', 'finalize', 'dashed', 'purple'),
        ('finalize', 'END', 'solid', 'black'),
    ]
    
    for start, end, style, color in arrows:
        x1, y1 = positions[start]
        x2, y2 = positions[end]
        
        if start == 'tools' and end == 'agent':
            arrow = FancyArrowPatch((x1+0.6, y1+0.2), (x2-0.6, y2-0.3),
                                   connectionstyle="arc3,rad=.5",
                                   arrowstyle='->',
                                   mutation_scale=25,
                                   linewidth=2.5,
                                   linestyle=style,
                                   color=color,
                                   zorder=2)
        else:
            arrow = FancyArrowPatch((x1, y1-0.4), (x2, y2+0.4 if end != 'tools' else y2+0.35),
                                   arrowstyle='->',
                                   mutation_scale=25,
                                   linewidth=2.5,
                                   linestyle=style,
                                   color=color,
                                   zorder=2)
        ax.add_patch(arrow)
    
    # Etichette
    ax.text(7, 6.5, 'Richiede\nanalisi\nmercato', fontsize=10, style='italic', color='blue',
           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    ax.text(7.5, 4.5, 'Ritorna\ndati\nfinanziari', fontsize=10, style='italic', color='green',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    ax.text(2.5, 4.5, 'Decide di\nfinalizzare', fontsize=10, style='italic', color='purple',
           bbox=dict(boxstyle='round', facecolor='plum', alpha=0.7))
    
    # Titolo
    plt.title('DAG Agente di Investimento\nArchitettura Agentica con Alpha Vantage MCP',
             fontsize=18, fontweight='bold', pad=20)
    
    # Legenda
    legend_elements = [
        mpatches.Patch(color='#87CEEB', label='Nodo Decisionale'),
        mpatches.Patch(color='#FFD700', label='Nodo Tools (MCP)'),
        mpatches.Patch(color='#FFA07A', label='Nodo Finalizzazione'),
        mpatches.Rectangle((0,0),1,1, linestyle='dashed', fill=False, label='Edge Condizionale'),
        mpatches.Rectangle((0,0),1,1, linestyle='solid', fill=False, label='Edge Diretto'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=11)
    
    # Descrizione tools
    tools_desc = (
        "🛠️ Tools Disponibili:\n"
        "• get_stock_quote\n"
        "• get_market_overview\n"
        "• analyze_sector_performance\n"
        "• calculate_portfolio_allocation"
    )
    ax.text(0.3, 7.5, tools_desc, fontsize=10,
           bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8),
           verticalalignment='top')
    
    plt.tight_layout()
    
    output_path = os.path.join(os.path.dirname(__file__), 'investment_agent_dag.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ DAG salvato in: {output_path}")
    
    plt.show()
    
    return output_path


def print_dag_info():
    """Stampa informazioni sul grafo."""
    print("\n" + "="*70)
    print("📊 ARCHITETTURA AGENTE DI INVESTIMENTO")
    print("="*70 + "\n")
    
    agent_app = create_investment_agent()
    graph = agent_app.get_graph()
    
    print("🔹 Nodi:")
    for node in graph.nodes:
        print(f"   - {node}")
    
    print("\n🔹 Flusso di Esecuzione:")
    print("""
    1. START → agent
       L'utente fornisce importo e profilo di rischio
    
    2. agent → tools (decisione autonoma)
       L'agente decide quali dati di mercato raccogliere
    
    3. tools → agent (loop)
       Esegue chiamate a Alpha Vantage MCP:
       - get_market_overview()
       - calculate_portfolio_allocation()
       - analyze_sector_performance()
       - get_stock_quote()
    
    4. agent → finalize
       Quando ha dati sufficienti, genera raccomandazioni
    
    5. finalize → END
       Output: portfolio allocation + rationale
    """)
    
    print("🎯 Caratteristiche:")
    print("   ✓ Integrazione MCP Alpha Vantage")
    print("   ✓ Analisi multi-asset (stocks, bonds, commodities)")
    print("   ✓ Profili di rischio personalizzati")
    print("   ✓ Decisioni basate su dati real-time")
    print("   ✓ Rationale dettagliato per ogni raccomandazione")
    
    # Genera anche il diagramma Mermaid
    print("\n" + "="*70)
    print("📄 Diagramma Mermaid:")
    print("="*70 + "\n")
    
    try:
        mermaid = agent_app.get_graph().draw_mermaid()
        print(mermaid)
        
        with open("investment_agent_mermaid.md", "w", encoding="utf-8") as f:
            f.write("# DAG Agente di Investimento\n\n```mermaid\n")
            f.write(mermaid)
            f.write("\n```\n")
        
        print("\n✅ Mermaid salvato in: investment_agent_mermaid.md")
    except Exception as e:
        print(f"⚠️ Errore Mermaid: {e}")


if __name__ == "__main__":
    print("🎨 Creazione visualizzazione DAG Agente di Investimento...\n")
    create_investment_dag_visual()
    print_dag_info()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

fig, ax = plt.subplots(1, 1, figsize=(20, 14))
ax.set_xlim(0, 20)
ax.set_ylim(0, 14)
ax.axis('off')
fig.patch.set_facecolor('#FAFBFC')

BLUE = '#1A56DB'
DARK_BLUE = '#0E3B8C'
LIGHT_BLUE = '#DBEAFE'
GREEN = '#059669'
LIGHT_GREEN = '#D1FAE5'
ORANGE = '#D97706'
LIGHT_ORANGE = '#FEF3C7'
PURPLE = '#7C3AED'
LIGHT_PURPLE = '#EDE9FE'
RED = '#DC2626'
LIGHT_RED = '#FEE2E2'
GRAY = '#6B7280'
LIGHT_GRAY = '#F3F4F6'
WHITE = '#FFFFFF'
TEAL = '#0D9488'
LIGHT_TEAL = '#CCFBF1'

def draw_box(ax, x, y, w, h, color, edge_color, text, fontsize=9, bold=False, alpha=1.0):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", facecolor=color, edgecolor=edge_color, linewidth=1.5, alpha=alpha)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fontsize, fontweight=weight, color='#1F2937', wrap=True)

def draw_section(ax, x, y, w, h, color, edge_color, title):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2", facecolor=color, edgecolor=edge_color, linewidth=2, alpha=0.4)
    ax.add_patch(box)
    ax.text(x + 0.3, y + h - 0.35, title, ha='left', va='top', fontsize=10, fontweight='bold', color=edge_color)

def draw_arrow(ax, x1, y1, x2, y2, color='#6B7280'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8, connectionstyle='arc3,rad=0'))

ax.text(10, 13.5, 'Reference Architecture: AI Banking Assistant', ha='center', va='center', fontsize=18, fontweight='bold', color=DARK_BLUE)
ax.text(10, 13.0, 'Day 1 Session 1 - RAG Applications + Snowflake Intelligence', ha='center', va='center', fontsize=12, color=GRAY)

draw_section(ax, 0.3, 9.5, 5.5, 3.0, LIGHT_ORANGE, ORANGE, 'DATA SOURCES')

draw_box(ax, 0.6, 11.2, 2.3, 0.8, WHITE, ORANGE, 'PDF Documents\n(SOP Bank)', fontsize=8, bold=True)
draw_box(ax, 3.2, 11.2, 2.3, 0.8, WHITE, ORANGE, 'CSV Files\n(Banking Data)', fontsize=8, bold=True)
draw_box(ax, 0.6, 10.0, 2.3, 0.8, WHITE, ORANGE, '6 SOP Documents\nKYC, AML, Kredit', fontsize=7)
draw_box(ax, 3.2, 10.0, 2.3, 0.8, WHITE, ORANGE, '5 Tables: Nasabah\nTransaksi, Kredit...', fontsize=7)

draw_section(ax, 6.3, 9.5, 7.5, 3.0, LIGHT_BLUE, BLUE, 'SNOWFLAKE PROCESSING')

draw_box(ax, 6.6, 11.2, 2.1, 0.8, WHITE, BLUE, 'PARSE_DOCUMENT\n(PDF to Text)', fontsize=7.5, bold=True)
draw_box(ax, 9.0, 11.2, 2.2, 0.8, WHITE, BLUE, 'SPLIT_TEXT\n(Chunking)', fontsize=7.5, bold=True)
draw_box(ax, 11.5, 11.2, 2.0, 0.8, WHITE, BLUE, 'COPY INTO\n(CSV Load)', fontsize=7.5, bold=True)

draw_box(ax, 6.6, 10.0, 2.1, 0.8, WHITE, BLUE, 'Internal Stage\n@STG_DOCUMENTS', fontsize=7)
draw_box(ax, 9.0, 10.0, 2.2, 0.8, WHITE, BLUE, 'DOC_CHUNKS\nTable', fontsize=7)
draw_box(ax, 11.5, 10.0, 2.0, 0.8, WHITE, BLUE, 'RAW Tables\n(5 Tables)', fontsize=7)

draw_section(ax, 0.3, 5.5, 6.5, 3.5, LIGHT_GREEN, GREEN, 'AI SERVICES')

draw_box(ax, 0.6, 7.5, 2.8, 1.0, WHITE, GREEN, 'Cortex Search\nService\n(Hybrid Search)', fontsize=8, bold=True)
draw_box(ax, 3.8, 7.5, 2.7, 1.0, WHITE, GREEN, 'Semantic View\n+\nCortex Analyst', fontsize=8, bold=True)
draw_box(ax, 0.6, 5.9, 2.8, 1.2, WHITE, GREEN, 'Unstructured\nSOP, KYC, AML\nKredit, Digital', fontsize=7)
draw_box(ax, 3.8, 5.9, 2.7, 1.2, WHITE, GREEN, 'Structured\nNPL, DPK, LDR\nTransaksi, Nasabah', fontsize=7)

draw_section(ax, 7.3, 5.5, 6.5, 3.5, LIGHT_PURPLE, PURPLE, 'CORTEX AGENT')

draw_box(ax, 7.6, 7.6, 5.9, 0.9, WHITE, PURPLE, 'AI Banking Assistant (Cortex Agent)\nOrchestrates all tools based on user questions', fontsize=9, bold=True)

draw_box(ax, 7.6, 6.1, 1.3, 1.1, WHITE, PURPLE, 'Cortex\nSearch\nTool', fontsize=7)
draw_box(ax, 9.1, 6.1, 1.3, 1.1, WHITE, PURPLE, 'Cortex\nAnalyst\nTool', fontsize=7)
draw_box(ax, 10.6, 6.1, 1.3, 1.1, WHITE, PURPLE, 'Web\nSearch\nTool', fontsize=7)
draw_box(ax, 12.1, 6.1, 1.3, 1.1, WHITE, PURPLE, 'Email\nSend\nTool', fontsize=7)

draw_section(ax, 14.3, 5.5, 5.3, 7.0, LIGHT_TEAL, TEAL, 'ANSWER TYPES')
draw_box(ax, 14.6, 10.7, 4.7, 1.1, WHITE, TEAL, 'Fact-Based Answer\n"Total DPK = Rp 2.5 Triliun"', fontsize=8, bold=True)
draw_box(ax, 14.6, 9.3, 4.7, 1.1, WHITE, TEAL, 'Diagnostic Answer\n"NPL naik 2% karena sektor F&B"', fontsize=8, bold=True)
draw_box(ax, 14.6, 7.9, 4.7, 1.1, WHITE, TEAL, 'Recommendation\n"Fokus restrukturisasi di Jawa Barat"', fontsize=8, bold=True)
draw_box(ax, 14.6, 6.5, 4.7, 1.1, WHITE, TEAL, 'Chart / Visualization\nBar, Line, Pie Charts', fontsize=8, bold=True)
draw_box(ax, 14.6, 5.8, 4.7, 0.5, WHITE, TEAL, 'Email Notification', fontsize=7.5)

draw_section(ax, 3.0, 0.5, 14.0, 4.5, LIGHT_RED, RED, 'SNOWFLAKE INTELLIGENCE (End Users)')

draw_box(ax, 3.5, 3.2, 3.5, 1.2, WHITE, RED, 'Relationship Manager\n"Ringkasan kredit UMKM\ndan SOP-nya?"', fontsize=8, bold=True)
draw_box(ax, 7.5, 3.2, 3.5, 1.2, WHITE, RED, 'Risk Analyst\n"NPL ratio per sektor\ndan rekomendasi?"', fontsize=8, bold=True)
draw_box(ax, 11.5, 3.2, 3.5, 1.2, WHITE, RED, 'Branch Manager\n"Performa cabang saya\nvs target?"', fontsize=8, bold=True)

draw_box(ax, 5.5, 1.0, 9.0, 1.5, WHITE, RED, 'Published Agent - Accessible via Snowflake Intelligence UI\nNo SQL knowledge required - Natural language interaction\nMulti-tool: SOP Search + Data Analytics + Web Search + Email', fontsize=9, bold=True)

draw_arrow(ax, 2.9, 11.6, 6.6, 11.6, ORANGE)
draw_arrow(ax, 5.5, 11.6, 11.5, 11.6, ORANGE)
draw_arrow(ax, 7.7, 11.2, 7.7, 10.8, BLUE)
draw_arrow(ax, 10.1, 11.2, 10.1, 10.8, BLUE)
draw_arrow(ax, 12.5, 11.2, 12.5, 10.8, BLUE)

draw_arrow(ax, 10.1, 10.0, 5.0, 8.5, GREEN)
draw_arrow(ax, 12.5, 10.0, 5.0, 8.0, GREEN)
draw_arrow(ax, 7.7, 10.0, 2.0, 8.5, GREEN)

draw_arrow(ax, 3.4, 7.5, 8.0, 7.2, PURPLE)
draw_arrow(ax, 5.2, 7.5, 9.5, 7.2, PURPLE)

draw_arrow(ax, 13.5, 8.0, 14.6, 8.4, TEAL)
draw_arrow(ax, 13.5, 7.0, 14.6, 7.0, TEAL)

draw_arrow(ax, 10.5, 6.1, 10.5, 4.4, RED)

fig.tight_layout()
out_path = os.path.join(os.path.dirname(__file__), "images", "architecture_day1_session1.png")
fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"Saved: {out_path}")
plt.close()


import os
import html
import streamlit as st
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

st.set_page_config(
    page_title="ResearchGraph AI | Research Workspace",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# DESIGN SYSTEM
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #f4f7fd;
  --surface: #ffffff;
  --ink: #14264c;
  --muted: #71809e;
  --line: #e4eaf5;
  --blue: #3867f6;
  --blue-dark: #204bc7;
  --violet: #8667f6;
  --teal: #12ad9a;
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
}
.stApp {
  background:
    radial-gradient(ellipse at 75% 0%, rgba(96,135,255,.10), transparent 36%),
    var(--bg);
  color: var(--ink);
}
[data-testid="stHeader"] {
  background: rgba(244,247,253,.85);
}
[data-testid="stToolbar"] { right: 1rem; }
#MainMenu, footer { visibility: hidden; }

.block-container {
  padding-top: 2rem;
  padding-bottom: 3rem;
  max-width: 1600px;
}
h1, h2, h3 {
  font-family: 'Manrope', sans-serif;
  color: var(--ink);
  letter-spacing: -.045em;
}
h1 { font-weight: 800; font-size: clamp(2rem, 3vw, 3rem); }
h2 { font-weight: 800; font-size: 1.55rem; }
h3 { font-weight: 700; font-size: 1.1rem; }
p, label, .stCaption { color: var(--muted); }

[data-testid="stSidebar"] {
  background: rgba(255,255,255,.97);
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] > div:first-child {
  padding-top: 1.5rem;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  font-size: .91rem;
}
[data-testid="stSidebar"] hr {
  border-color: var(--line);
  margin: 1.2rem 0;
}
[data-testid="stSidebar"] [role="radiogroup"] {
  gap: 5px;
}
[data-testid="stSidebar"] [role="radiogroup"] label {
  background: transparent;
  padding: 10px 12px;
  border-radius: 11px;
  transition: background .2s ease, transform .2s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {
  background: #eef3ff;
  transform: translateX(3px);
}
[data-testid="stSidebar"] [role="radiogroup"] label p {
  color: #354969;
  font-weight: 600;
}
[data-testid="stSidebar"] [role="radiogroup"] > label > div:first-child {
  display: none;
}

[data-testid="stMetric"] {
  background: rgba(255,255,255,.92);
  border: 1px solid var(--line);
  border-radius: 17px;
  padding: 19px 20px;
  box-shadow: 0 7px 25px rgba(40,68,120,.045);
  transition: transform .23s ease, box-shadow .23s ease;
  animation: rise .55s ease both;
}
[data-testid="stMetric"]:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 30px rgba(40,68,120,.09);
}
[data-testid="stMetricLabel"] {
  color: var(--muted);
  font-weight: 600;
}
[data-testid="stMetricValue"] {
  color: var(--ink);
  font-family: 'Manrope', sans-serif;
  font-weight: 800;
}

.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
  border-radius: 12px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(56,103,246,.12) !important;
}
.stButton > button, .stDownloadButton > button {
  border-radius: 11px;
  border: 1px solid #dfe7f7;
  font-weight: 700;
  transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-2px);
  border-color: #9eb7ff;
  box-shadow: 0 7px 18px rgba(56,103,246,.11);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(110deg, #3867f6, #6d63f5);
  color: white;
  border: none;
}
[data-testid="stDataFrame"] {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
}
[data-testid="stExpander"] {
  border: 1px solid var(--line);
  border-radius: 13px;
  background: white;
}
[data-testid="stAlert"] { border-radius: 12px; }

.brand {
  font: 800 1.3rem 'Manrope', sans-serif;
  color: #172d5a;
  letter-spacing: -.05em;
}
.brand-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  margin-right: 9px;
  border-radius: 13px;
  color: white;
  font-size: 22px;
  background: linear-gradient(135deg, #3867f6, #9275ff);
  box-shadow: 0 8px 18px rgba(74,99,228,.24);
  vertical-align: middle;
}
.eyebrow {
  color: #6480b2;
  text-transform: uppercase;
  letter-spacing: .13em;
  font-size: .72rem;
  font-weight: 800;
  margin-bottom: .5rem;
}
.hero {
  position: relative;
  overflow: hidden;
  padding: 27px 30px;
  border-radius: 21px;
  color: white;
  background: linear-gradient(120deg, #142b59 0%, #3159c9 65%, #7064e8 100%);
  box-shadow: 0 14px 35px rgba(39,69,150,.18);
  animation: rise .5s ease both;
}
.hero h2 { color: white; font-size: clamp(1.5rem, 2.4vw, 2.15rem); }
.hero p { color: #e0e8ff; }
.hero-orb {
  position: absolute;
  width: 210px;
  height: 210px;
  right: -40px;
  top: -85px;
  border-radius: 50%;
  background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.16);
}
.hero-orb.two {
  width: 130px;
  height: 130px;
  right: 100px;
  top: 75px;
}
.panel {
  background: rgba(255,255,255,.96);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 21px;
  box-shadow: 0 8px 26px rgba(40,68,120,.035);
  transition: transform .22s ease, box-shadow .22s ease;
  animation: rise .55s ease both;
}
.panel:hover {
  box-shadow: 0 13px 32px rgba(40,68,120,.075);
}
.panel-title {
  color: var(--ink);
  font: 800 1.12rem 'Manrope', sans-serif;
}
.panel-subtitle {
  color: var(--muted);
  font-size: .86rem;
  margin-top: 4px;
}
.tag {
  display: inline-block;
  margin: 3px 4px 3px 0;
  padding: 6px 10px;
  color: #3158bd;
  background: #eaf0ff;
  border: 1px solid #e0e9ff;
  border-radius: 30px;
  font-size: .76rem;
  font-weight: 700;
}
.empty {
  border: 1px dashed #ccd8ef;
  background: #f8faff;
  border-radius: 15px;
  padding: 27px;
  text-align: center;
  color: var(--muted);
}
.mini-label {
  color: var(--muted);
  font-size: .8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
}
.paper-title {
  font: 700 1rem 'Manrope', sans-serif;
  color: #1c376c;
}
.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background: #20bd8a;
  border-radius: 50%;
  margin-right: 7px;
  box-shadow: 0 0 0 4px #e4f8f0;
}
@keyframes rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation: none !important;
    transition: none !important;
    scroll-behavior: auto !important;
  }
}
@media (max-width: 850px) {
  .block-container { padding: 1.1rem; }
  .panel { padding: 15px; }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE
# =========================================================
@st.cache_resource
def get_driver():
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not all([uri, username, password]):
        raise ValueError("Missing Neo4j settings in .env")

    return GraphDatabase.driver(uri, auth=(username, password))


def load_data():
    driver = get_driver()
    database = os.getenv("NEO4J_DATABASE")

    with driver.session(database=database) as session:
        counts = session.run("""
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->()
            RETURN count(DISTINCT n) AS nodes,
                   count(r) AS relationships
        """).single()

        papers = session.run("""
            MATCH (p:Paper)
            RETURN p.id AS id, p.title AS title, p.year AS year,
                   p.domain AS domain, p.abstract AS abstract,
                   p.doi AS doi, p.source_url AS source_url,
                   p.publication_type AS publication_type
            ORDER BY p.year DESC, p.title
        """).data()

        labels = session.run("""
            MATCH (n)
            UNWIND labels(n) AS label
            RETURN label, count(*) AS total
            ORDER BY total DESC
        """).data()

        concepts = session.run("""
            MATCH (c:Concept)
            RETURN c.name AS name ORDER BY c.name
        """).data()

        authors = session.run("""
            MATCH (a:Author)
            RETURN a.id AS id, a.name AS name ORDER BY a.name
        """).data()

        nodes = session.run("""
            MATCH (n)
            RETURN elementId(n) AS id, labels(n) AS labels,
                   coalesce(n.title, n.name, n.id, 'Node') AS label
            LIMIT 70
        """).data()

        edges = session.run("""
            MATCH (a)-[r]->(b)
            RETURN elementId(a) AS source, elementId(b) AS target,
                   type(r) AS relation
            LIMIT 120
        """).data()

    return counts, papers, labels, concepts, authors, nodes, edges


def esc(value):
    return html.escape(str(value or ""))


def render_tags(values):
    if not values:
        st.caption("No concepts have been added yet.")
        return
    st.markdown(
        "".join(f'<span class="tag">{esc(x)}</span>' for x in values),
        unsafe_allow_html=True,
    )


def render_graph(nodes, edges):
    if not nodes:
        st.markdown(
            '<div class="empty">🕸️<br><br><b>Your knowledge graph is ready to grow.</b>'
            '<br>Add research records to visualize connections here.</div>',
            unsafe_allow_html=True,
        )
        return

    try:
        import graphviz
        graph = graphviz.Digraph()
        graph.attr(
            rankdir="LR",
            bgcolor="transparent",
            overlap="false",
            splines="true",
            pad="0.3",
            nodesep="0.55",
            ranksep="0.85",
        )
        graph.attr("node", style="filled,rounded", shape="box",
                   fontname="Arial", fontsize="10", margin="0.16,0.12",
                   color="#dbe5f7", penwidth="1.2")
        graph.attr("edge", color="#b9c9e8", fontname="Arial",
                   fontsize="8", fontcolor="#65799c", arrowsize="0.65")

        colors = {
            "Paper": "#dce8ff",
            "Author": "#d7f4e8",
            "Concept": "#ebe2ff",
            "Method": "#ffe7d7",
        }
        valid = set()
        for n in nodes:
            valid.add(n["id"])
            label_type = n["labels"][0] if n["labels"] else "Node"
            graph.node(
                n["id"],
                label=f'{n["label"]}\n{label_type}',
                fillcolor=colors.get(label_type, "#edf1f8"),
                fontcolor="#1a315d",
            )
        for e in edges:
            if e["source"] in valid and e["target"] in valid:
                graph.edge(e["source"], e["target"], label=e["relation"])
        st.graphviz_chart(graph, use_container_width=True)
    except Exception:
        st.warning("The graph renderer is unavailable. Install graphviz with pip if needed.")
        st.dataframe(
            [{"Node": n["label"], "Type": ", ".join(n["labels"])} for n in nodes],
            use_container_width=True,
        )


# =========================================================
# SIDEBAR / NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown(
        '<div style="padding:0 0 8px 0">'
        '<span class="brand-icon">⌘</span>'
        '<span class="brand">ResearchGraph AI</span></div>',
        unsafe_allow_html=True,
    )
    st.caption("Connect ideas. Discover knowledge.")
    st.divider()
    st.markdown('<div class="mini-label">WORKSPACE</div>', unsafe_allow_html=True)

    pages = [
        "Overview",
        "Discover Papers",
        "Knowledge Graph",
        "AI Research Assistant",
        "Collections",
        "Literature Review",
        "Settings",
    ]
    page_icons = {
        "Overview": "◈",
        "Discover Papers": "▤",
        "Knowledge Graph": "⌘",
        "AI Research Assistant": "✧",
        "Collections": "▱",
        "Literature Review": "▥",
        "Settings": "⚙",
    }

    if "page" not in st.session_state:
        st.session_state.page = "Overview"

    page = st.radio(
        "Navigation",
        pages,
        format_func=lambda x: f'{page_icons[x]}    {x}',
        label_visibility="collapsed",
        key="page",
    )

    st.divider()
    st.markdown('<div class="mini-label">CONNECTION</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="padding:10px 0"><span class="status-dot"></span>'
        '<b style="color:#24436e">Neo4j Aura</b><br>'
        '<span style="color:#8391a9;font-size:.8rem">Research workspace connected</span></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("ResearchGraph AI")
    st.caption("Evidence first. Discovery always.")


# =========================================================
# LOAD DATABASE SAFELY
# =========================================================
try:
    counts, papers, labels, concepts, authors, nodes, edges = load_data()
except Exception as error:
    st.markdown(
        '<div class="hero"><div class="hero-orb"></div><div class="hero-orb two"></div>'
        '<h2>Welcome to ResearchGraph AI</h2>'
        '<p>Your research workspace is ready. We could not load the database right now.</p></div>',
        unsafe_allow_html=True,
    )
    st.error("Database request failed. Check the Neo4j connection and .env configuration.")
    st.code(str(error))
    st.stop()


# =========================================================
# TOP HEADER / SEARCH
# =========================================================
top_a, top_b = st.columns([5, 1])
with top_a:
    st.markdown('<div class="eyebrow">YOUR RESEARCH COMMAND CENTER</div>',
                unsafe_allow_html=True)
with top_b:
    st.markdown(
        '<div style="text-align:right;padding-top:5px;color:#7485a4">'
        '✦ Research workspace</div>',
        unsafe_allow_html=True,
    )

search = st.text_input(
    "Search",
    placeholder="⌕   Search papers, authors, concepts, methods...",
    label_visibility="collapsed",
    key="global_search",
)

filtered_papers = [
    p for p in papers
    if not search or search.lower() in " ".join(
        str(p.get(k) or "") for k in
        ["id", "title", "domain", "abstract", "doi"]
    ).lower()
]

author_count = sum(x["total"] for x in labels if x["label"] == "Author")
concept_count = sum(x["total"] for x in labels if x["label"] == "Concept")


# =========================================================
# OVERVIEW
# =========================================================
if page == "Overview":
    st.markdown(
        '<div class="hero"><div class="hero-orb"></div><div class="hero-orb two"></div>'
        '<div class="eyebrow" style="color:#cbd9ff">RESEARCH WORKSPACE</div>'
        '<h2>Discover the connections<br>behind the research.</h2>'
        '<p>Explore scientific papers, connect ideas, and build knowledge from evidence.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    a, b, c, d = st.columns(4)
    a.metric("Papers Indexed", len(papers), help="Paper records stored in Neo4j")
    b.metric("Authors", author_count)
    c.metric("Concepts", concept_count)
    d.metric("Research Connections", counts["relationships"])

    st.write("")
    left, right = st.columns([1.8, 1], gap="large")

    with left:
        st.markdown("### 🕸️ Knowledge Graph")
        st.caption("A connected view of your research universe.")
        with st.container(border=True):
            render_graph(nodes, edges)
            st.caption(
                f'{counts["nodes"]} nodes · {counts["relationships"]} relationships'
            )
            if st.button("Open graph workspace →", type="primary",
                         use_container_width=True):
                st.session_state.page = "Knowledge Graph"
                st.rerun()

    with right:
        st.markdown("### ✦ Research Insights")
        with st.container(border=True):
            st.markdown("**Concepts in your graph**")
            render_tags([x["name"] for x in concepts if x.get("name")][:15])
            st.divider()
            st.markdown("**Latest paper records**")
            if filtered_papers:
                for paper in filtered_papers[:5]:
                    st.markdown(
                        f'<div style="padding:8px 0;border-bottom:1px solid #edf1f8">'
                        f'<div class="paper-title">{esc(paper.get("title") or "Untitled")}</div>'
                        f'<div class="panel-subtitle">{esc(paper.get("year") or "Year unknown")} '
                        f'· {esc(paper.get("domain") or "Unclassified")}</div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No papers match this search.")
            if st.button("Discover papers →", use_container_width=True):
                st.session_state.page = "Discover Papers"
                st.rerun()

    st.write("")
    st.markdown("### Recent Research Papers")
    st.caption("Records currently stored in your connected knowledge graph.")

    if filtered_papers:
        st.dataframe(
            [
                {
                    "Title": p.get("title"),
                    "Year": p.get("year"),
                    "Domain": p.get("domain") or "Unclassified",
                    "Type": p.get("publication_type") or "Not specified",
                }
                for p in filtered_papers
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.markdown('<div class="empty">No matching papers were found.</div>',
                    unsafe_allow_html=True)


# =========================================================
# DISCOVER PAPERS
# =========================================================
elif page == "Discover Papers":
    st.markdown('<div class="eyebrow">LITERATURE EXPLORER</div>',
                unsafe_allow_html=True)
    st.title("Discover Papers")
    st.caption("Search, filter, and inspect research records from your knowledge graph.")

    years = sorted(
        {p["year"] for p in papers if p.get("year") is not None},
        reverse=True,
    )
    f1, f2 = st.columns([1, 2])
    with f1:
        year_filter = st.selectbox("Publication year", ["All years"] + years)
    with f2:
        domain_values = sorted(
            {p.get("domain") or "Unclassified" for p in papers}
        )
        domain_filter = st.selectbox("Research domain", ["All domains"] + domain_values)

    result_papers = [
        p for p in filtered_papers
        if (year_filter == "All years" or p.get("year") == year_filter)
        and (domain_filter == "All domains"
             or (p.get("domain") or "Unclassified") == domain_filter)
    ]

    st.markdown(f"**{len(result_papers)} records found**")
    if result_papers:
        st.dataframe(
            [
                {
                    "ID": p.get("id"),
                    "Title": p.get("title"),
                    "Year": p.get("year"),
                    "Domain": p.get("domain") or "Unclassified",
                }
                for p in result_papers
            ],
            use_container_width=True,
            hide_index=True,
        )

        options = {
            f'{p.get("title") or "Untitled"} · {p.get("id")}': p
            for p in result_papers
        }
        chosen = st.selectbox("Open paper details", list(options))
        p = options[chosen]
        with st.container(border=True):
            st.markdown(f"### {p.get('title') or 'Untitled paper'}")
            st.caption(f"Record ID: {p.get('id') or 'Unknown'}")
            x, y, z = st.columns(3)
            x.metric("Year", p.get("year") or "Unknown")
            y.metric("Domain", p.get("domain") or "Unclassified")
            z.metric("Record type", p.get("publication_type") or "Unspecified")
            st.markdown("**Abstract**")
            st.write(p.get("abstract") or "No abstract has been stored.")
            if p.get("doi"):
                st.write("**DOI:**", p["doi"])
            if p.get("source_url"):
                st.link_button("Open source publication ↗", p["source_url"])
    else:
        st.markdown('<div class="empty">No papers match your filters.</div>',
                    unsafe_allow_html=True)


# =========================================================
# KNOWLEDGE GRAPH
# =========================================================
elif page == "Knowledge Graph":
    st.markdown('<div class="eyebrow">CONNECTED KNOWLEDGE</div>',
                unsafe_allow_html=True)
    st.title("Knowledge Graph")
    st.caption("Explore the entities and relationships stored in Neo4j.")

    x, y, z = st.columns(3)
    x.metric("Nodes", counts["nodes"])
    y.metric("Relationships", counts["relationships"])
    z.metric("Visible graph nodes", len(nodes))

    with st.container(border=True):
        render_graph(nodes, edges)

    st.markdown("### Graph records")
    st.dataframe(
        [
            {
                "Node": n["label"],
                "Type": ", ".join(n["labels"]),
                "Database element ID": n["id"],
            }
            for n in nodes
        ],
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# AI RESEARCH ASSISTANT
# =========================================================
elif page == "AI Research Assistant":
    st.markdown('<div class="eyebrow">EVIDENCE-GROUNDED DISCOVERY</div>',
                unsafe_allow_html=True)
    st.title("AI Research Assistant")
    st.caption("A research assistant that will answer using traceable graph evidence.")

    st.markdown(
        '<div class="hero"><div class="hero-orb"></div>'
        '<h2>Ask better research questions.</h2>'
        '<p>Explore ideas across papers, authors, concepts and methods.</p></div>',
        unsafe_allow_html=True,
    )
    st.write("")
    st.info(
        "The AI answer-generation pipeline is not connected yet. "
        "This page is a designed workspace, not a functioning AI chatbot yet."
    )
    question = st.text_area(
        "Research question",
        placeholder="Example: Which papers study knowledge graphs, and what methods do they use?",
    )
    if st.button("Prepare research query", type="primary"):
        if question.strip():
            st.session_state["research_question"] = question.strip()
            st.success("Question saved for the next AI integration step.")
            st.write("Your question:", question)
            st.caption("Next: retrieve relevant Neo4j evidence and cite its source records.")
        else:
            st.warning("Enter a question first.")

    st.markdown("### Try these research questions")
    for example in [
        "Which papers discuss knowledge graphs?",
        "Which authors are connected to each paper?",
        "Which research methods appear in the graph?",
    ]:
        st.markdown(f'<span class="tag">{esc(example)}</span>',
                    unsafe_allow_html=True)


# =========================================================
# COLLECTIONS
# =========================================================
elif page == "Collections":
    st.markdown('<div class="eyebrow">ORGANIZE YOUR DISCOVERY</div>',
                unsafe_allow_html=True)
    st.title("Research Collections")
    st.caption("A workspace for saved papers and curated reading lists.")

    st.markdown(
        '<div class="panel"><div class="panel-title">Your library starts here</div>'
        '<div class="panel-subtitle">Saved collections are not stored in the database yet. '
        'We will add persistent collections after the paper workflow is ready.</div></div>',
        unsafe_allow_html=True,
    )
    st.metric("Available paper records", len(papers))


# =========================================================
# LITERATURE REVIEW
# =========================================================
elif page == "Literature Review":
    st.markdown('<div class="eyebrow">SYNTHESIS WORKSPACE</div>',
                unsafe_allow_html=True)
    st.title("Literature Review")
    st.caption("Prepare a structured review from your research collection.")

    st.info(
        "Automated synthesis is not implemented yet. We should first import real papers "
        "with verified abstracts and source links so that any generated review is evidence-based."
    )

    if papers:
        st.markdown("### Papers currently available")
        st.dataframe(
            [
                {
                    "Title": p.get("title"),
                    "Year": p.get("year"),
                    "Domain": p.get("domain") or "Unclassified",
                    "Source URL": p.get("source_url") or "Not available",
                }
                for p in papers
            ],
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# SETTINGS
# =========================================================
elif page == "Settings":
    st.markdown('<div class="eyebrow">WORKSPACE CONFIGURATION</div>',
                unsafe_allow_html=True)
    st.title("Settings")
    st.caption("Database status and application diagnostics.")

    with st.container(border=True):
        st.markdown("### Database connection")
        st.markdown(
            '<span class="status-dot"></span><b>Neo4j Aura</b> · Connected',
            unsafe_allow_html=True,
        )
        st.write("Configured database:", os.getenv("NEO4J_DATABASE", "Not configured"))
        st.write("Paper records:", len(papers))
        st.write("Graph nodes:", counts["nodes"])
        st.write("Relationships:", counts["relationships"])
        st.caption("Secrets are not displayed in this interface.")

        if st.button("Verify connection", type="primary"):
            try:
                get_driver().verify_connectivity()
                st.success("Neo4j connectivity verified.")
            except Exception:
                st.error("Verification failed. Check the local configuration.")


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#93a0b7;font-size:.8rem;padding:8px">'
    'ResearchGraph AI · Connect ideas. Discover knowledge. · '
    'Research data shown here comes from your connected Neo4j database.'
    '</div>',
    unsafe_allow_html=True,
)

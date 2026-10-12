import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity, AlertCircle, ArrowDownUp, ArrowRight, BookOpen,
  Check, ChevronDown, ChevronLeft, ChevronRight, CircleHelp,
  Command, Database, Download, FileText, Filter, FlaskConical,
  Folder, GitBranch, GraduationCap, Layers3, LoaderCircle, Network,
  Plus, RefreshCw, Search, Settings2, ShieldCheck, Sparkles, Trash2,
  Upload, Users, X, ZoomIn, ZoomOut, Maximize2,
} from 'lucide-react'
import { api } from './api'
import './App.css'

const navigation = [
  { label: 'Overview', icon: Layers3 },
  { label: 'Discover papers', icon: Search },
  { label: 'Knowledge graph', icon: Network },
  { label: 'Research assistant', icon: Sparkles },
  { label: 'Compare papers', icon: ArrowDownUp },
  { label: 'Research gaps', icon: FlaskConical },
  { label: 'Collections', icon: Folder },
  { label: 'Import data', icon: Upload },
  { label: 'Settings', icon: Settings2 },
]

const typeColors = {
  Paper: 'violet',
  Author: 'cyan',
  Concept: 'blue',
  Method: 'amber',
}

function displayTitle(properties = {}) {
  return properties.title || properties.name || properties.id || 'Untitled record'
}

function Property({ label, value, multiline = false }) {
  return (
    <div className={`property ${multiline ? 'property-wide' : ''}`}>
      <dt>{label}</dt>
      <dd>{value === null || value === undefined || value === '' ? 'Not available in the current record.' : String(value)}</dd>
    </div>
  )
}

function App() {
  const [activePage, setActivePage] = useState('Overview')
  const [health, setHealth] = useState(null)
  const [stats, setStats] = useState(null)
  const [statsError, setStatsError] = useState('')
  const [globalSearch, setGlobalSearch] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)
  const [notice, setNotice] = useState('')

  const refresh = useCallback(() => setRefreshKey((key) => key + 1), [])
  const notify = useCallback((message) => {
    setNotice(message)
    window.setTimeout(() => setNotice(''), 3200)
  }, [])

  useEffect(() => {
    let alive = true
    api.health().then((data) => alive && setHealth(data)).catch((error) => alive && setHealth({ status: 'disconnected', error: error.message }))
    api.stats().then((data) => {
      if (alive) {
        setStats(data)
        setStatsError('')
      }
    }).catch((error) => {
      if (alive) {
        setStats(null)
        setStatsError(error.message)
      }
    })
    return () => { alive = false }
  }, [refreshKey])

  function navigateToSearch() {
    setActivePage('Discover papers')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => setActivePage('Overview')} aria-label="ResearchGraph AI home">
          <span className="brand-symbol"><Network size={19} /></span>
          <span><strong>ResearchGraph</strong><small>RESEARCH WORKSPACE</small></span>
        </button>

        <div className="workspace-switcher">
          <span className="workspace-avatar"><GraduationCap size={16} /></span>
          <span><strong>Research workspace</strong><small>Personal · Local</small></span>
          <ChevronDown size={15} />
        </div>

        <div className="nav-heading">WORKSPACE</div>
        <nav className="nav-list" aria-label="Main navigation">
          {navigation.map(({ label, icon: Icon }) => (
              <button key={label} aria-label={label} aria-current={activePage === label ? 'page' : undefined} className={`nav-item ${activePage === label ? 'active' : ''}`} onClick={() => setActivePage(label)}>
              <Icon size={17} strokeWidth={1.8} /><span>{label}</span>
              {label === 'Research assistant' && <span className="nav-note">Evidence</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-spacer" />
        <div className="sidebar-status">
          <span className={`health-dot ${health?.status === 'connected' ? 'online' : ''}`} />
          <span><strong>{health?.status === 'connected' ? 'Neo4j connected' : 'Database unavailable'}</strong><small>{health?.status === 'connected' ? health.database : 'Check API and connection'}</small></span>
          <button className="bare-icon" aria-label="Refresh connection" onClick={refresh}><RefreshCw size={15} /></button>
        </div>
        <div className="profile-row">
          <div className="profile-avatar">R</div><span><strong>Researcher</strong><small>Local workspace</small></span>
          <button className="bare-icon" onClick={() => setActivePage('Settings')} aria-label="Open settings"><Settings2 size={16} /></button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><ChevronRight size={14} /><strong>{activePage}</strong></div>
          <div className="topbar-actions">
            <form className="global-search" onSubmit={(event) => { event.preventDefault(); navigateToSearch() }}>
              <Search size={16} /><input aria-label="Search connected research" placeholder="Search connected research…" value={globalSearch} onChange={(event) => setGlobalSearch(event.target.value)} />
              <kbd><Command size={11} /> K</kbd>
            </form>
            <span className={`connection-pill ${health?.status === 'connected' ? 'is-online' : ''}`}><i />{health?.status === 'connected' ? 'Connected' : 'Offline'}</span>
            <button className="bare-icon refresh-button" aria-label="Refresh data" onClick={refresh}><RefreshCw size={16} /></button>
          </div>
        </header>

        <div className="page-content">
          {activePage === 'Overview' && <Overview stats={stats} statsError={statsError} health={health} setActivePage={setActivePage} setGlobalSearch={setGlobalSearch} search={globalSearch} refreshKey={refreshKey} onRetry={refresh} />}
          {activePage === 'Discover papers' && <Discover key={globalSearch} search={globalSearch} refreshKey={refreshKey} notify={notify} />}
          {activePage === 'Knowledge graph' && <GraphWorkspace refreshKey={refreshKey} />}
          {activePage === 'Research assistant' && <Assistant />}
          {activePage === 'Compare papers' && <Compare refreshKey={refreshKey} />}
          {activePage === 'Research gaps' && <Gaps refreshKey={refreshKey} />}
          {activePage === 'Collections' && <Collections refreshKey={refreshKey} notify={notify} />}
          {activePage === 'Import data' && <ImportData />}
          {activePage === 'Settings' && <Settings health={health} stats={stats} refreshKey={refreshKey} />}
        </div>
      </main>
      {notice && <div className="toast" role="status"><Check size={16} />{notice}</div>}
    </div>
  )
}

function PageHeading({ eyebrow, title, description, action }) {
  return (
    <div className="page-heading">
      <div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>
      {action}
    </div>
  )
}

function Loading({ label = 'Loading research data…' }) {
  return <div className="state-box"><LoaderCircle className="spin" size={22} /><span>{label}</span></div>
}

function ErrorState({ error, retry }) {
  return <div className="state-box state-error"><AlertCircle size={20} /><span>{error}</span>{retry && <button className="button secondary small" onClick={retry}>Retry</button>}</div>
}

function EmptyState({ title, description }) {
  return <div className="empty-state"><span className="empty-icon"><BookOpen size={19} /></span><strong>{title}</strong><p>{description}</p></div>
}

function Overview({ stats, statsError, health, setActivePage, setGlobalSearch, search, refreshKey, onRetry }) {
  const [papers, setPapers] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    let alive = true
    api.papers({ limit: 5, search }).then((data) => alive && setPapers(data.papers)).catch((err) => alive && setError(err.message))
    return () => { alive = false }
  }, [search, refreshKey])

  return (
    <>
      <PageHeading eyebrow="RESEARCH INTELLIGENCE" title="Your research, connected." description="A live view of the records and relationships in your research graph." action={<span className={`status-pill ${health?.status === 'connected' ? 'good' : 'bad'}`}><span />{health?.status === 'connected' ? 'Database live' : 'Database unavailable'}</span>} />
      {stats ? (
        <>
          <div className="metric-grid">
            <Metric icon={BookOpen} label="Papers" value={stats.papers} color="violet" note="Indexed records" />
            <Metric icon={Users} label="Authors" value={stats.authors} color="cyan" note="Graph entities" />
            <Metric icon={Sparkles} label="Concepts" value={stats.concepts} color="blue" note="Graph entities" />
            <Metric icon={FlaskConical} label="Methods" value={stats.methods} color="amber" note="Graph entities" />
            <Metric icon={GitBranch} label="Relationships" value={stats.total_relationships} color="green" note={`${stats.total_nodes} total nodes`} />
          </div>
          <div className="overview-grid">
            <section className="panel">
              <div className="panel-heading"><div><span className="section-label">CONNECTED RECORDS</span><h2>Papers in graph</h2></div><button className="button secondary small" onClick={() => setActivePage('Discover papers')}>Browse papers <ArrowRight size={14} /></button></div>
              {error ? <ErrorState error={error} /> : papers === null ? <Loading /> : papers.length ? <div className="paper-table">
                {papers.map((paper) => <PaperRow key={paper.element_id || paper.id} paper={paper} onClick={() => { setGlobalSearch(displayTitle(paper.properties || paper)); setActivePage('Discover papers') }} />)}
              </div> : <EmptyState title="No papers found" description="This view searches records in your connected Neo4j database only." />}
            </section>
            <section className="panel insight-panel">
              <div className="panel-heading"><div><span className="section-label">GRAPH INVENTORY</span><h2>Entity types</h2></div><button className="bare-icon" onClick={() => setActivePage('Knowledge graph')} aria-label="Open graph"><ArrowRight size={17} /></button></div>
              <div className="entity-list">
                {Object.entries(stats.nodes_by_label || {}).map(([label, count]) => <div className="entity-item" key={label}><span className={`entity-dot ${typeColors[label] || ''}`} /><span>{label}</span><strong>{count}</strong></div>)}
              </div>
              <div className="divider" />
              <div className="relationship-summary"><span className="section-label">RELATIONSHIPS</span>{Object.entries(stats.relationships_by_type || {}).map(([type, count]) => <div key={type}><span>{type.replaceAll('_', ' ').toLowerCase()}</span><strong>{count}</strong></div>)}</div>
            </section>
          </div>
          <div className="notice-banner"><ShieldCheck size={17} /><span><strong>Evidence first.</strong> Statistics and records above come from the connected graph; sample records are not substituted.</span><button className="bare-icon" aria-label="Open settings" onClick={() => setActivePage('Settings')}><ArrowRight size={16} /></button></div>
        </>
      ) : <ErrorState error={statsError || 'Could not load live graph statistics.'} retry={onRetry} />}
    </>
  )
}

function Metric({ icon: Icon, label, value, color, note }) {
  return <div className="metric-card"><div className={`metric-icon ${color}`}><Icon size={17} /></div><div className="metric-copy"><span>{label}</span><strong>{value ?? '—'}</strong><small>{note}</small></div></div>
}

function PaperRow({ paper, onClick }) {
  const properties = paper.properties || paper
  const labels = paper.labels || ['Paper']
  const title = displayTitle(properties)
  const isSample = String(properties.source_type || '').toLowerCase() === 'sample'
  return <button className="paper-row" onClick={onClick}><span className={`paper-badge ${typeColors[labels[0]] || 'violet'}`}><FileText size={17} /></span><span className="paper-row-copy"><strong>{title}</strong><small>{properties.year || 'Year not recorded'}{properties.domain ? ` · ${properties.domain}` : ''}{properties.doi ? ` · DOI ${properties.doi}` : ''}</small></span>{isSample && <span className="source-tag">Sample · unverified</span>}<ArrowRight size={16} className="muted-icon" /></button>
}

function Discover({ search, refreshKey, notify }) {
  const [query, setQuery] = useState(search)
  const [papers, setPapers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState(null)
  const [offset, setOffset] = useState(0)
  const [sort, setSort] = useState('title')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.papers({ search: query, limit: 25, offset, sort })
      setPapers(data.papers)
      setError('')
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }, [query, offset, sort])

  useEffect(() => {
    let active = true
    api.papers({ search: query, limit: 25, offset, sort })
      .then((data) => {
        if (active) {
          setPapers(data.papers)
          setError('')
        }
      })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [query, offset, sort, refreshKey])
  return (
    <>
      <PageHeading eyebrow="CONNECTED LIBRARY" title="Discover papers" description="Search and inspect the research records in your connected database." />
      <div className="panel search-results-panel">
        <form className="discover-tools" onSubmit={(event) => { event.preventDefault(); setError(''); setLoading(true); if (offset === 0) load(); else setOffset(0) }}>
          <label className="search-input"><Search size={17} /><input value={query} onChange={(event) => { setError(''); setLoading(true); setQuery(event.target.value); setOffset(0) }} placeholder="Search title, abstract, DOI, domain or author" aria-label="Search database papers" /></label>
          <label className="select-wrap"><ArrowDownUp size={15} /><select value={sort} onChange={(event) => setSort(event.target.value)} aria-label="Sort paper results"><option value="title">Title A–Z</option><option value="year">Year (newest)</option></select></label>
          <button className="button primary" type="submit"><Search size={15} /> Search</button>
        </form>
        <div className="result-meta"><span>{loading ? 'Searching database…' : `${papers.length} records on this page`}</span><span><Database size={14} /> Connected database only</span></div>
        {error ? <ErrorState error={error} retry={() => { setError(''); setLoading(true); load() }} /> : loading ? <Loading /> : papers.length ? <div className="paper-table">
          {papers.map((paper) => <PaperRow key={paper.element_id || paper.id} paper={paper} onClick={() => setSelected(paper)} />)}
        </div> : <EmptyState title="No matching records" description="Try another title, author, DOI, abstract, or domain search." />}
        <div className="pager"><button className="button secondary small" disabled={!offset || loading} onClick={() => { setLoading(true); setOffset(Math.max(0, offset - 25)) }}><ChevronLeft size={15} /> Previous</button><span>Page {Math.floor(offset / 25) + 1}</span><button className="button secondary small" disabled={papers.length < 25 || loading} onClick={() => { setLoading(true); setOffset(offset + 25) }}>Next <ChevronRight size={15} /></button></div>
      </div>
      {selected && <Modal title={displayTitle(selected.properties || selected)} close={() => setSelected(null)}>
        <PaperDetail paper={selected} notify={notify} />
      </Modal>}
    </>
  )
}

function PaperDetail({ paper, notify }) {
  const properties = paper.properties || paper
  const id = paper.id || properties.id || paper.element_id
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState('')
  const [collections, setCollections] = useState([])
  useEffect(() => {
    let alive = true
    api.paper(id).then((value) => alive && setDetail(value)).catch((err) => alive && setError(err.message))
    api.collections().then((value) => alive && setCollections(value.collections)).catch(() => {})
    return () => { alive = false }
  }, [id])

  async function saveToCollection(collectionId) {
    try {
      await api.addToCollection(collectionId, id)
      notify('Paper saved to collection.')
    } catch (err) { setError(err.message) }
  }

  const entityProperties = detail?.properties || properties
  return <div className="detail-content">
    {error && <ErrorState error={error} />}
    <dl className="properties-grid">
      <Property label="Year" value={entityProperties.year} />
      <Property label="Domain" value={entityProperties.domain} />
      <Property label="Publication type" value={entityProperties.publication_type} />
      <Property label="Source type / provenance" value={entityProperties.source_type} />
      <Property label="DOI" value={entityProperties.doi} />
      <Property label="Abstract" value={entityProperties.abstract} multiline />
      <Property label="Source" value={entityProperties.source_url} multiline />
    </dl>
    {entityProperties.source_url && <a className="button secondary" href={entityProperties.source_url} target="_blank" rel="noreferrer">Open source record <ArrowRight size={14} /></a>}
    <h3 className="subheading">Connected records</h3>
    {detail ? detail.connections.length ? <div className="connection-list">{detail.connections.map((connection) => <div className="connection-chip" key={`${connection.id}-${connection.relationship}`}><span className={`entity-dot ${typeColors[connection.labels?.[0]] || ''}`} />{displayTitle(connection.properties)}<small>{connection.relationship?.replaceAll('_', ' ').toLowerCase()}</small></div>)}</div> : <p className="muted-text">No connected records in the current graph.</p> : <Loading label="Loading linked records…" />}
    {collections.length > 0 && <label className="save-paper-select">Save to collection<select defaultValue="" onChange={(event) => event.target.value && saveToCollection(event.target.value)}><option value="" disabled>Select a collection</option>{collections.map((collection) => <option value={collection.id} key={collection.id}>{collection.name}</option>)}</select></label>}
  </div>
}

function GraphWorkspace({ refreshKey }) {
  const [graph, setGraph] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState('All types')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(null)
  const [zoom, setZoom] = useState(1)
  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try { setGraph(await api.graph(100)); setError('') } catch (err) { setError(err.message) } finally { setLoading(false) }
  }, [])
  useEffect(() => {
    let active = true
    api.graph(100)
      .then((data) => { if (active) { setGraph(data); setError('') } })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [refreshKey])

  const nodes = useMemo(() => (graph?.nodes || []).filter((node) => {
    const kind = node.labels?.[0] || 'Other'
    const title = displayTitle(node.properties).toLowerCase()
    return (typeFilter === 'All types' || kind === typeFilter) && (!query || title.includes(query.toLowerCase()))
  }), [graph, typeFilter, query])
  const nodeById = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes])
  const edges = useMemo(() => (graph?.edges || []).filter((edge) => nodeById.has(edge.source) && nodeById.has(edge.target)), [graph, nodeById])
  const connectedNodeIds = useMemo(() => {
    if (!selected) return new Set()
    return new Set([
      selected.id,
      ...edges.flatMap((edge) => edge.source === selected.id ? [edge.target] : edge.target === selected.id ? [edge.source] : []),
    ])
  }, [edges, selected])
  const positions = useMemo(() => {
    const centerX = 480
    const centerY = 310
    const radiusX = 360
    const radiusY = 230
    return new Map(nodes.map((node, index) => {
      const angle = (2 * Math.PI * index / Math.max(nodes.length, 1)) - Math.PI / 2
      return [node.id, { x: centerX + radiusX * Math.cos(angle), y: centerY + radiusY * Math.sin(angle) }]
    }))
  }, [nodes])

  return (
    <>
      <PageHeading eyebrow="LIVE NEO4J DATA" title="Knowledge graph" description="Browse a bounded graph sample from the connected database. Select an entity to inspect its stored properties." action={<button className="button secondary" onClick={() => { setError(''); setLoading(true); load() }}><RefreshCw size={15} /> Refresh graph</button>} />
      <div className="graph-toolbar panel">
        <label className="search-input graph-search"><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Focus by entity name" aria-label="Search graph entities" /></label>
        <label className="select-wrap"><Filter size={15} /><select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)} aria-label="Filter graph entity types"><option>All types</option>{['Paper', 'Author', 'Concept', 'Method'].map((type) => <option key={type}>{type}</option>)}</select></label>
        <span className="graph-count">{nodes.length} nodes · {edges.length} relationships{graph?.truncated ? ' · sample limited' : ''}</span>
        <div className="zoom-controls" aria-label="Graph zoom controls"><button className="bare-icon" aria-label="Zoom out" onClick={() => setZoom((value) => Math.max(0.65, value - 0.15))}><ZoomOut size={15} /></button><span>{Math.round(zoom * 100)}%</span><button className="bare-icon" aria-label="Zoom in" onClick={() => setZoom((value) => Math.min(1.6, value + 0.15))}><ZoomIn size={15} /></button><button className="bare-icon" aria-label="Reset graph zoom" onClick={() => setZoom(1)}><Maximize2 size={14} /></button></div>
      </div>
      {error ? <ErrorState error={error} retry={load} /> : loading ? <Loading /> : graph?.nodes.length === 0 ? <EmptyState title="The graph has no nodes" description="No graph entities were returned by the connected database." /> : (
        <div className="graph-layout">
          <div className="graph-canvas-wrap">
            <div className="graph-canvas-scroll">
              <svg className="graph-canvas" style={{ width: `${zoom * 100}%` }} viewBox="0 0 960 620" role="img" aria-label="Interactive graph of database entities and relationships">
                <defs><marker id="edge-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#596478" /></marker></defs>
                {edges.map((edge) => {
                  const source = positions.get(edge.source)
                  const target = positions.get(edge.target)
                  if (!source || !target) return null
                  const highlighted = !selected || edge.source === selected.id || edge.target === selected.id
                  return <g className={`graph-edge ${highlighted ? 'highlighted' : 'dimmed'}`} key={edge.id}><line x1={source.x} y1={source.y} x2={target.x} y2={target.y} markerEnd="url(#edge-arrow)" /><text x={(source.x + target.x) / 2} y={(source.y + target.y) / 2 - 5}>{edge.type}</text></g>
                })}
                {nodes.map((node) => {
                  const point = positions.get(node.id)
                  const kind = node.labels?.[0] || 'Other'
                  return <g key={node.id} className={`graph-node ${selected?.id === node.id ? 'selected' : selected && !connectedNodeIds.has(node.id) ? 'dimmed' : ''}`} transform={`translate(${point.x} ${point.y})`} tabIndex="0" role="button" aria-label={`${kind}: ${displayTitle(node.properties)}`} onClick={() => setSelected(node)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') setSelected(node) }}>
                    <circle r="28" className={`node-circle ${typeColors[kind] || 'blue'}`} />
                    <text className="node-type" y="-3">{kind}</text>
                    <text className="node-label" y="46">{displayTitle(node.properties).slice(0, 30)}</text>
                  </g>
                })}
              </svg>
            </div>
            <div className="graph-legend">{['Paper', 'Author', 'Concept', 'Method'].map((type) => <span key={type}><i className={`entity-dot ${typeColors[type]}`} />{type}</span>)}</div>
          </div>
          <aside className="node-details panel">
            {selected ? <>
              <div className="panel-heading"><div><span className="section-label">SELECTED ENTITY</span><h2>{displayTitle(selected.properties)}</h2></div><button className="bare-icon" onClick={() => setSelected(null)} aria-label="Clear selected entity"><X size={16} /></button></div>
              <span className={`type-tag ${typeColors[selected.labels?.[0]] || ''}`}>{selected.labels?.join(' · ') || 'Node'}</span>
              <dl className="node-properties">{Object.entries(selected.properties || {}).map(([key, value]) => <Property key={key} label={key.replaceAll('_', ' ')} value={typeof value === 'object' ? JSON.stringify(value) : value} />)}</dl>
              <div className="node-connections"><span className="section-label">CONNECTED ENTITY IDS</span>{edges.filter((edge) => edge.source === selected.id || edge.target === selected.id).map((edge) => <div key={edge.id}>{edge.type.replaceAll('_', ' ')} <small>{displayTitle((nodeById.get(edge.source === selected.id ? edge.target : edge.source) || {}).properties)}</small></div>)}</div>
            </> : <EmptyState title="Select a node" description="Click a graph entity to inspect its actual properties and connections." />}
          </aside>
        </div>
      )}
    </>
  )
}

function Assistant() {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  async function ask(value = question) {
    if (!value.trim()) return
    setQuestion(value)
    setLoading(true)
    setError('')
    try { setResult(await api.assistant(value)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const suggestions = ['Which records discuss a specific concept?', 'What papers mention a particular method?', 'Which authors are represented in the graph?']
  return (
    <>
      <PageHeading eyebrow="DATABASE EVIDENCE RETRIEVAL" title="Research assistant" description="Retrieve matching records from your graph. This is not an LLM and does not search the web." />
      <div className="assistant-layout">
        <section className="panel assistant-main">
          <div className="assistant-notice"><CircleHelp size={16} /><span><strong>Transparent mode.</strong> The API matches question terms against stored graph properties and returns sources. It does not generate answers.</span></div>
          <form className="assistant-form" onSubmit={(event) => { event.preventDefault(); ask() }}>
            <label htmlFor="research-question">Ask about records in this graph</label>
            <textarea id="research-question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="For example: Which papers discuss machine learning methods?" maxLength={500} />
            <div className="form-footer"><span>{question.length}/500</span><button className="button primary" disabled={loading || !question.trim()}><Sparkles size={15} /> Retrieve evidence</button></div>
          </form>
          <div className="suggestion-list"><span className="section-label">SUGGESTED QUERIES</span>{suggestions.map((item) => <button key={item} onClick={() => ask(item)}>{item}<ArrowRight size={14} /></button>)}</div>
          {error && <ErrorState error={error} />}
          {loading && <Loading label="Searching stored graph properties…" />}
          {result && !loading && <div className="evidence-results"><div className="result-meta"><strong>{result.count} matching records</strong><span>Terms: {result.terms.join(', ')}</span></div><p className="muted-text">{result.notice}</p>{result.sources.length ? result.sources.map((source) => <div className="evidence-source" key={source.id}><span className={`entity-dot ${typeColors[source.labels?.[0]] || ''}`} /><div><strong>{displayTitle(source.properties)}</strong><small>{source.labels.join(' · ')} · ID {source.id}</small></div></div>) : <EmptyState title="No matching evidence" description="Try a word present in a paper title, abstract, DOI, author, concept, or method property." />}</div>}
        </section>
        <aside className="panel assistant-side"><div className="icon-tile violet"><ShieldCheck size={19} /></div><h2>Evidence, not invention.</h2><p>Results quote stored records only. No generated findings, external citations, or claims are added.</p><div className="divider" /><div className="capability"><Check size={15} /> Traceable database matches</div><div className="capability"><Check size={15} /> Source properties shown verbatim</div><div className="capability"><X size={15} /> No LLM or web search configured</div></aside>
      </div>
    </>
  )
}

function Compare({ refreshKey }) {
  const [papers, setPapers] = useState([])
  const [selected, setSelected] = useState([])
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  useEffect(() => {
    api.papers({ limit: 100 }).then((data) => setPapers(data.papers)).catch((err) => setError(err.message))
  }, [refreshKey])
  function toggle(id) {
    setSelected((items) => items.includes(id) ? items.filter((item) => item !== id) : items.length < 4 ? [...items, id] : items)
    setComparison(null)
  }
  async function compare() {
    setLoading(true)
    setError('')
    try { setComparison(await api.compare(selected)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  return <>
    <PageHeading eyebrow="SIDE-BY-SIDE EVIDENCE" title="Compare papers" description="Select two to four records; missing fields are shown explicitly and no conclusions are invented." />
    {error && <ErrorState error={error} />}
    <section className="panel selection-panel"><div className="panel-heading"><div><span className="section-label">PAPER SELECTION</span><h2>{selected.length} selected · choose 2–4</h2></div><button className="button primary" disabled={selected.length < 2 || loading} onClick={compare}><ArrowDownUp size={15} /> Compare</button></div>
      {papers.length ? <div className="select-paper-list">{papers.map((paper) => { const properties = paper.properties || paper; const id = paper.id || properties.id || paper.element_id; return <label className="paper-checkbox" key={id}><input type="checkbox" checked={selected.includes(id)} onChange={() => toggle(id)} disabled={!selected.includes(id) && selected.length >= 4} /><span className="paper-badge violet"><FileText size={16} /></span><span><strong>{displayTitle(properties)}</strong><small>{properties.year || 'Year not recorded'} · {id}</small></span></label> })}</div> : <Loading label="Loading graph papers…" />}
    </section>
    {loading && <Loading label="Comparing available properties…" />}
    {comparison && <div className="comparison-grid">{comparison.papers.map((paper) => <section className="panel comparison-card" key={paper.id}><span className="section-label">{paper.properties.year || 'YEAR NOT RECORDED'}{String(paper.properties.source_type || '').toLowerCase() === 'sample' ? ' · SAMPLE / UNVERIFIED' : ''}</span><h2>{displayTitle(paper.properties)}</h2><dl>{comparison.fields.map((field) => <Property key={field} label={field.replaceAll('_', ' ')} value={paper.properties[field]} multiline={['abstract', 'limitations', 'findings'].includes(field)} />)}</dl></section>)}</div>}
  </>
}

function Gaps({ refreshKey }) {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const load = useCallback(async () => { setLoading(true); setError(''); try { setData(await api.gaps()); setError('') } catch (err) { setError(err.message) } finally { setLoading(false) } }, [])
  useEffect(() => {
    let active = true
    api.gaps()
      .then((value) => { if (active) { setData(value); setError('') } })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [refreshKey])
  return <>
    <PageHeading eyebrow="GRAPH-BOUNDED EXPLORATION" title="Candidate research gaps" description="Surface concepts with few linked papers in this local graph—signals for investigation, not proven gaps." />
    <div className="notice-banner warning"><AlertCircle size={17} /><span><strong>Limited scope.</strong> Findings describe only your indexed records and should not be generalized to the research literature as a whole.</span></div>
    {error ? <ErrorState error={error} retry={() => { setError(''); setLoading(true); load() }} /> : loading ? <Loading /> : data?.candidates.length ? <div className="gap-list">{data.candidates.map((candidate) => <section className="panel gap-card" key={candidate.id}><div className="gap-score">{candidate.paper_count}<small>linked papers</small></div><div className="gap-copy"><span className="section-label">CONCEPT · {candidate.id}</span><h2>{displayTitle(candidate.concept)}</h2><p>{candidate.paper_count === 0 ? 'No linked paper records found in this graph.' : 'Few linked paper records found in this graph.'}</p><div className="connection-list">{candidate.papers.map((paper) => <span className="connection-chip" key={paper.id || paper.title}>{paper.title || paper.id || 'Paper record'}</span>)}</div></div></section>)}</div> : <EmptyState title="No concept candidates found" description="No Concept nodes are currently available in the connected graph." />}
    <p className="scope-note">{data?.scope}</p>
  </>
}

function Collections({ refreshKey, notify }) {
  const [collections, setCollections] = useState([])
  const [papers, setPapers] = useState([])
  const [name, setName] = useState('')
  const [rename, setRename] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const [collectionData, paperData] = await Promise.all([api.collections(), api.papers({ limit: 100 })])
      setError('')
      setCollections(collectionData.collections)
      setPapers(paperData.papers)
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }, [])
  useEffect(() => {
    let active = true
    Promise.all([api.collections(), api.papers({ limit: 100 })])
      .then(([collectionData, paperData]) => {
        if (active) {
          setCollections(collectionData.collections)
          setPapers(paperData.papers)
          setError('')
        }
      })
      .catch((err) => { if (active) setError(err.message) })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [refreshKey])

  async function create(event) {
    event.preventDefault()
    try { await api.createCollection(name); setName(''); await load(); notify('Collection created.') } catch (err) { setError(err.message) }
  }
  async function changeName(collection) {
    const next = rename[collection.id]
    if (!next?.trim()) return
    try { await api.renameCollection(collection.id, next); await load(); notify('Collection renamed.') } catch (err) { setError(err.message) }
  }
  async function remove(collection) {
    if (!window.confirm(`Delete collection “${collection.name}”? Its saved links will be removed; paper records stay untouched.`)) return
    try { await api.deleteCollection(collection.id); await load(); notify('Collection deleted.') } catch (err) { setError(err.message) }
  }
  async function add(collectionId, paperId) {
    if (!paperId) return
    try { await api.addToCollection(collectionId, paperId); await load(); notify('Paper saved to collection.') } catch (err) { setError(err.message) }
  }
  async function removePaper(collectionId, paperId) {
    try { await api.removeFromCollection(collectionId, paperId); await load(); notify('Paper removed from collection.') } catch (err) { setError(err.message) }
  }
  const paperById = useMemo(() => new Map(papers.map((paper) => [paper.id, paper])), [papers])

  return <>
    <PageHeading eyebrow="SAVED RESEARCH" title="Collections" description="Organize selected paper IDs in a separate local SQLite store. Your Neo4j records are never modified." />
    <form className="panel create-collection" onSubmit={create}><label className="search-input"><Folder size={16} /><input value={name} onChange={(event) => setName(event.target.value)} placeholder="Name a collection" aria-label="New collection name" maxLength={80} /></label><button className="button primary" disabled={!name.trim()}><Plus size={16} /> Create collection</button></form>
    {error && <ErrorState error={error} />}
    {loading ? <Loading /> : collections.length ? <div className="collection-list">{collections.map((collection) => <section className="panel collection-card" key={collection.id}><div className="panel-heading"><div><span className="section-label">{collection.paper_count} SAVED PAPERS</span><h2>{collection.name}</h2></div><button className="button danger small" onClick={() => remove(collection)}><Trash2 size={14} /> Delete</button></div>
      <div className="collection-actions"><label className="search-input"><input value={rename[collection.id] ?? ''} onChange={(event) => setRename((state) => ({ ...state, [collection.id]: event.target.value }))} placeholder="New collection name" aria-label={`New name for ${collection.name}`} maxLength={80} /></label><button className="button secondary small" disabled={!rename[collection.id]?.trim()} onClick={() => changeName(collection)}>Rename</button><select defaultValue="" onChange={(event) => add(collection.id, event.target.value)} aria-label={`Add a paper to ${collection.name}`}><option value="" disabled>Add a database paper…</option>{papers.map((paper) => <option key={paper.id} value={paper.id}>{displayTitle(paper.properties || paper)}</option>)}</select></div>
      {collection.paper_ids.length ? <div className="saved-papers">{collection.paper_ids.map((id) => <div className="saved-paper" key={id}><span>{displayTitle(paperById.get(id)?.properties || paperById.get(id) || { title: `Record ${id}` })}</span><button className="bare-icon" aria-label="Remove saved paper" onClick={() => removePaper(collection.id, id)}><X size={15} /></button></div>)}</div> : <p className="muted-text">No papers saved in this collection yet.</p>}
    </section>)}</div> : <EmptyState title="No collections yet" description="Create a collection to save links to existing database papers." />}
  </>
}

function ImportData() {
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  async function readFile(file) {
    if (!file) return
    setLoading(true)
    setError('')
    setPreview(null)
    try {
      const content = await file.text()
      setPreview(await api.importPreview(file.name, content))
    } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  return <>
    <PageHeading eyebrow="SAFE FILE VALIDATION" title="Import data" description="Validate a scholarly CSV or JSON file before considering a separately reviewed import workflow." />
    <section className="panel import-panel">
      <label className="upload-zone"><input type="file" accept=".csv,.json,application/json,text/csv" onChange={(event) => readFile(event.target.files?.[0])} /><span className="upload-icon"><Upload size={21} /></span><strong>Choose a CSV or JSON file</strong><small>CSV with headers or a JSON object/list · 2 MB maximum</small><span className="button secondary"><Download size={14} /> Browse files</span></label>
      <div className="supported-fields"><span className="section-label">SUPPORTED FIELDS</span><p>Required: <code>title</code>. Optional: <code>id</code>, <code>abstract</code>, <code>year</code>, <code>doi</code>, <code>source_url</code>, <code>domain</code>, <code>publication_type</code>, <code>keywords</code>, <code>methodology</code>, <code>dataset</code>, <code>findings</code>, <code>limitations</code>.</p></div>
      <div className="assistant-notice"><ShieldCheck size={16} /><span><strong>Preview only.</strong> This endpoint validates structure and returns warnings. It does not write records to Neo4j.</span></div>
    </section>
    {loading && <Loading label="Validating file preview…" />}
    {error && <ErrorState error={error} />}
    {preview && <section className="panel preview-panel"><div className="panel-heading"><div><span className="section-label">{preview.format.toUpperCase()} · PREVIEW ONLY</span><h2>{preview.filename}</h2></div><span className="status-pill good"><span />{preview.valid_count} valid rows</span></div><p className="muted-text">No database writes made. {preview.invalid_count} invalid rows · {preview.warnings.length} warnings.</p>{preview.errors.map((item, index) => <div className="import-error" key={index}><AlertCircle size={15} />Row {item.row}: {item.message}</div>)}{preview.warnings.map((item, index) => <div className="import-warning" key={index}><AlertCircle size={15} />Row {item.row}: ignored unsupported columns ({item.ignored_fields.join(', ')})</div>)}<div className="preview-records">{preview.records.map((record, index) => <pre key={index}>{JSON.stringify(record, null, 2)}</pre>)}</div>{preview.records_truncated && <p className="muted-text">Showing first 20 valid rows.</p>}</section>}
  </>
}

function Settings({ health, stats, refreshKey }) {
  const [status, setStatus] = useState(null)
  useEffect(() => { api.health().then((value) => setStatus(value)).catch((err) => setStatus({ status: 'disconnected', error: err.message })) }, [refreshKey])
  return <>
    <PageHeading eyebrow="WORKSPACE CONFIGURATION" title="Settings" description="Connection and capability status without revealing credentials." />
    <section className="panel settings-panel"><div className="panel-heading"><div><span className="section-label">SERVICES</span><h2>Connectivity</h2></div></div><div className="setting-row"><span className="setting-icon"><Activity size={17} /></span><span><strong>FastAPI service</strong><small>Configured API base URL</small></span><span className="status-pill good"><span />Reachable</span></div><div className="setting-row"><span className="setting-icon"><Database size={17} /></span><span><strong>Neo4j Aura</strong><small>{status?.database || health?.database || 'Server-reported database'}</small></span><span className={`status-pill ${status?.status === 'connected' ? 'good' : 'bad'}`}><span />{status?.status === 'connected' ? 'Connected' : 'Unavailable'}</span></div>
      {status?.error && <ErrorState error={status.error} />}
      <div className="divider" /><span className="section-label">LIVE ENTITY COUNTS</span><div className="settings-counts">{Object.entries(stats?.nodes_by_label || {}).map(([label, count]) => <div key={label}><span>{label}</span><strong>{count}</strong></div>)}</div>
      <div className="divider" /><span className="section-label">AVAILABLE CAPABILITIES</span><div className="capability-grid"><Capability name="Database search" state="Available" /><Capability name="Interactive graph" state="Available" /><Capability name="Local collections" state="SQLite persistence" /><Capability name="Import" state="CSV/JSON preview only" /><Capability name="Research assistant" state="Evidence retrieval; no LLM" /><Capability name="User accounts" state="Not configured" /></div>
    </section>
    <p className="muted-text version-note">ResearchGraph AI API v1.0.0 · This local development setup has not been hardened for public production deployment.</p>
  </>
}

function Capability({ name, state }) {
  return <div className="capability-row"><Check size={14} /><span>{name}</span><small>{state}</small></div>
}

function Modal({ title, close, children }) {
  useEffect(() => {
    function onKey(event) { if (event.key === 'Escape') close() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [close])
  return <div className="modal-overlay" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) close() }}><section className="modal" role="dialog" aria-modal="true" aria-label={title}><div className="modal-header"><div><span className="section-label">PAPER RECORD</span><h2>{title}</h2></div><button className="bare-icon" onClick={close} aria-label="Close paper details"><X size={18} /></button></div>{children}</section></div>
}

export default App

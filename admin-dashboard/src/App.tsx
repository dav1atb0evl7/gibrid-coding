import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import { Activity, ArrowDownToLine, ArrowUpRight, BriefcaseBusiness, Check, ChevronDown, CircleDot, Clock3, Command, LayoutDashboard, LockKeyhole, LogOut, Menu, Plus, RefreshCw, Search, Settings2, Users, X } from 'lucide-react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'
type Order = { public_id: string; service: string; description: string; budget: string; deadline: string; contact: string; status: string; internal_notes: string | null; assigned_to: string | null; created_at: string; client_name: string; username: string | null; telegram_id: number }
type Counts = Record<string, number>
const statusList = ['NEW', 'CONTACTED', 'NEGOTIATION', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']

function App() {
    const [token, setToken] = useState(sessionStorage.getItem('gxc-admin-token') || '')
    const [draftToken, setDraftToken] = useState('')
    const [counts, setCounts] = useState<Counts | null>(null)
    const [orders, setOrders] = useState<Order[]>([])
    const [clients, setClients] = useState<Array<Record<string, string | number | null>>>([])
    const [tab, setTab] = useState<'orders' | 'clients'>('orders')
    const [search, setSearch] = useState('')
    const [filter, setFilter] = useState('ALL')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [selected, setSelected] = useState<Order | null>(null)
    const [mobileNav, setMobileNav] = useState(false)

    async function api<T>(path: string, init?: RequestInit): Promise<T> {
        const response = await fetch(`${API}${path}`, { ...init, headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json', ...init?.headers } })
        if (!response.ok) throw new Error(response.status === 401 ? 'Access token was not accepted.' : `Request failed (${response.status}).`)
        return response.json() as Promise<T>
    }

    async function load() {
        if (!token) return
        setLoading(true); setError('')
        try {
            const [summary, orderRows, clientRows] = await Promise.all([api<Counts>('/api/admin/dashboard'), api<Order[]>('/api/admin/orders'), api<Array<Record<string, string | number | null>>>('/api/admin/clients')])
            setCounts(summary); setOrders(orderRows); setClients(clientRows)
        } catch (caught) { setError(caught instanceof Error ? caught.message : 'Could not load the dashboard.') }
        finally { setLoading(false) }
    }

    useEffect(() => { void load() }, [token])

    async function signIn(event: FormEvent) {
        event.preventDefault(); sessionStorage.setItem('gxc-admin-token', draftToken); setToken(draftToken)
    }

    async function updateOrder(order: Order, patch: Partial<Pick<Order, 'status' | 'internal_notes' | 'assigned_to'>>) {
        try {
            const updated = await api<Order>(`/api/admin/orders/${order.public_id}`, { method: 'PATCH', body: JSON.stringify(patch) })
            setOrders(rows => rows.map(row => row.public_id === order.public_id ? updated : row)); setSelected(updated); await load()
        } catch (caught) { setError(caught instanceof Error ? caught.message : 'Could not update order.') }
    }

    const visibleOrders = orders.filter(order => (filter === 'ALL' || order.status === filter) && `${order.public_id} ${order.service} ${order.client_name} ${order.username || ''}`.toLowerCase().includes(search.toLowerCase()))

    if (!token) return <main className="login-screen"><form className="login-panel" onSubmit={signIn}><div className="brand-mark">GX<span>/</span></div><p className="eyebrow">GIBRID X CODING · OPERATIONS</p><h1>Command<br />the details.</h1><p className="muted">Sign in with your admin API key to continue.</p><label className="field-label" htmlFor="token">Admin API key</label><input id="token" autoComplete="current-password" type="password" value={draftToken} onChange={event => setDraftToken(event.target.value)} required /><button className="primary-button" type="submit"><LockKeyhole size={16} /> Secure sign in</button></form><div className="login-foot">INTERNAL SYSTEM <span>●</span> ENCRYPTED SESSION</div></main>

    return <div className="app-shell">
        <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
            <div className="side-brand"><div className="brand-mark small">GX<span>/</span></div><div><strong>GIBRID <i>X</i> CODING</strong><small>OPERATIONS</small></div><button className="icon-button mobile-close" onClick={() => setMobileNav(false)} aria-label="Close navigation"><X size={17} /></button></div>
            <div className="workspace-label">WORKSPACE <ChevronDown size={13} /></div>
            <nav><button className="nav-item active"><LayoutDashboard size={17} /> Overview</button><button className={`nav-item ${tab === 'orders' ? 'selected' : ''}`} onClick={() => setTab('orders')}><BriefcaseBusiness size={17} /> Projects <span className="nav-count">{counts?.new_orders || 0}</span></button><button className={`nav-item ${tab === 'clients' ? 'selected' : ''}`} onClick={() => setTab('clients')}><Users size={17} /> Clients</button><button className="nav-item" onClick={() => setError('Catalog management is available through the deployment API.')}><Command size={17} /> Service catalog</button></nav>
            <div className="sidebar-bottom"><div className="system-status"><span className="pulse" /> ALL SYSTEMS OPERATIONAL<small>API CONNECTED</small></div><button className="nav-item" onClick={() => setError('Broadcast and settings are managed by the bot administrator.')}><Settings2 size={17} /> Settings</button><button className="account-row" onClick={() => { sessionStorage.removeItem('gxc-admin-token'); setToken(''); setCounts(null) }}><div className="avatar">GX</div><div><strong>Administrator</strong><small>Authorized access</small></div><LogOut size={16} /></button></div>
        </aside>
        {mobileNav && <button className="nav-scrim" onClick={() => setMobileNav(false)} aria-label="Close navigation" />}
        <main className="main-area">
            <header className="topbar"><button className="icon-button menu-button" onClick={() => setMobileNav(true)} aria-label="Open navigation"><Menu size={19} /></button><div className="breadcrumbs">Workspace <span>/</span> <b>Overview</b></div><div className="top-actions"><span className="live-indicator"><i /> LIVE</span><button className="icon-button" onClick={() => void load()} title="Refresh data" aria-label="Refresh data"><RefreshCw size={16} /></button><button className="user-chip" title="Sign out" onClick={() => { sessionStorage.removeItem('gxc-admin-token'); setToken('') }}>GX</button></div></header>
            <div className="content">
                <section className="page-heading"><div><p className="eyebrow">MONDAY, OCTOBER 05, 2026 <span>·</span> LIVE OPERATIONS</p><h1>Overview<span className="accent-dot">.</span></h1><p className="muted">A clear view of what's moving across your business.</p></div><button className="outline-button" onClick={() => void load()}><ArrowDownToLine size={15} /> Export view</button></section>
                {error && <div className="notice"><span>{error}</span><button onClick={() => setError('')} aria-label="Dismiss"><X size={15} /></button></div>}
                <section className="metric-grid">
                    <Metric label="Total users" value={counts?.total_users} icon={<Users size={16} />} tone="blue" note="Telegram audience" />
                    <Metric label="Clients" value={counts?.total_clients} icon={<BriefcaseBusiness size={16} />} tone="red" note="Qualified records" />
                    <Metric label="New requests" value={counts?.new_orders} icon={<CircleDot size={16} />} tone="amber" note="Awaiting review" />
                    <Metric label="Active projects" value={counts?.active_projects} icon={<Activity size={16} />} tone="green" note="In delivery" />
                    <Metric label="Completed" value={counts?.completed_projects} icon={<Check size={16} />} tone="blue" note="Successfully shipped" />
                    <Metric label="Cancelled" value={counts?.cancelled_orders} icon={<X size={16} />} tone="muted" note="Closed requests" />
                </section>
                <section className="work-section">
                    <div className="section-top"><div><p className="eyebrow">PIPELINE</p><h2>{tab === 'orders' ? 'Project requests' : 'Client directory'} <span>{tab === 'orders' ? orders.length : clients.length}</span></h2></div><div className="table-actions"><label className="search-box"><Search size={15} /><input value={search} onChange={event => setSearch(event.target.value)} placeholder={tab === 'orders' ? 'Search projects...' : 'Search clients...'} /></label><button className="filter-button" onClick={() => setFilter(filter === 'ALL' ? 'NEW' : 'ALL')}><CircleDot size={14} /> {filter === 'ALL' ? 'All statuses' : 'New only'} <ChevronDown size={13} /></button></div></div>
                    <div className="tab-row"><button className={tab === 'orders' ? 'tab-active' : ''} onClick={() => setTab('orders')}>Orders <span>{orders.length}</span></button><button className={tab === 'clients' ? 'tab-active' : ''} onClick={() => setTab('clients')}>Clients <span>{clients.length}</span></button></div>
                    {tab === 'orders' ? <div className="table-wrap"><table><thead><tr><th>PROJECT</th><th>CLIENT</th><th>SERVICE</th><th>BUDGET</th><th>STATUS</th><th>RECEIVED</th><th /></tr></thead><tbody>{visibleOrders.map(order => <tr key={order.public_id} onClick={() => setSelected(order)}><td><strong className="order-id">{order.public_id}</strong><small className="sub-cell">{order.deadline}</small></td><td><strong>{order.client_name}</strong><small className="sub-cell">{order.username ? `@${order.username}` : order.telegram_id}</small></td><td>{order.service}</td><td>{order.budget}</td><td><Status value={order.status} /></td><td className="date-cell">{new Date(order.created_at).toLocaleDateString()}</td><td><button className="row-action" aria-label="Open project"><ArrowUpRight size={15} /></button></td></tr>)}</tbody></table>{visibleOrders.length === 0 && <Empty loading={loading} />}</div> : <div className="table-wrap"><table><thead><tr><th>CLIENT</th><th>TELEGRAM</th><th>LANGUAGE</th><th>PHONE</th><th>JOINED</th></tr></thead><tbody>{clients.filter(client => `${client.first_name} ${client.username}`.toLowerCase().includes(search.toLowerCase())).map(client => <tr key={client.telegram_id}><td><strong>{client.first_name}</strong></td><td>{client.username ? `@${client.username}` : client.telegram_id}</td><td>{client.language?.toString().toUpperCase()}</td><td>{client.phone || '—'}</td><td>{client.registered_at ? new Date(client.registered_at).toLocaleDateString() : '—'}</td></tr>)}</tbody></table>{clients.length === 0 && <Empty loading={loading} />}</div>}
                    <footer className="table-footer"><span>Showing {tab === 'orders' ? visibleOrders.length : clients.length} records</span><span><Clock3 size={13} /> Updated just now</span></footer>
                </section>
                <footer className="page-footer"><span>GXC OPERATIONS <b>·</b> PRIVATE WORKSPACE</span><span>API <i className="online-dot" /> CONNECTED</span></footer>
            </div>
        </main>
        {selected && <div className="modal-backdrop" onClick={() => setSelected(null)}><section className="detail-panel" onClick={event => event.stopPropagation()}><div className="panel-head"><div><p className="eyebrow">PROJECT REQUEST</p><h2>{selected.public_id}</h2></div><button className="icon-button" onClick={() => setSelected(null)} aria-label="Close project"><X size={18} /></button></div><Status value={selected.status} /><div className="detail-block"><span>SERVICE</span><strong>{selected.service}</strong></div><div className="detail-block"><span>PROJECT BRIEF</span><p>{selected.description}</p></div><div className="detail-pair"><div className="detail-block"><span>BUDGET</span><strong>{selected.budget}</strong></div><div className="detail-block"><span>DEADLINE</span><strong>{selected.deadline}</strong></div></div><div className="detail-block"><span>CLIENT</span><strong>{selected.client_name} {selected.username && `(@${selected.username})`}</strong><a href={`https://t.me/${selected.username || ''}`}>{selected.contact}</a></div><label className="field-label" htmlFor="status">Update status</label><select id="status" value={selected.status} onChange={event => void updateOrder(selected, { status: event.target.value })}>{statusList.map(status => <option key={status}>{status}</option>)}</select><label className="field-label" htmlFor="notes">Internal notes</label><textarea id="notes" defaultValue={selected.internal_notes || ''} placeholder="Add a note for your team" onBlur={event => { if (event.target.value !== (selected.internal_notes || '')) void updateOrder(selected, { internal_notes: event.target.value }) }} /><label className="field-label" htmlFor="assignee">Assigned to</label><input id="assignee" defaultValue={selected.assigned_to || ''} placeholder="Staff member" onBlur={event => { if (event.target.value !== (selected.assigned_to || '')) void updateOrder(selected, { assigned_to: event.target.value }) }} /></section></div>}
    </div>
}

function Metric({ label, value, icon, tone, note }: { label: string; value?: number; icon: ReactNode; tone: string; note: string }) {
    return <article className="metric"><div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone}`}>{icon}</span></div><strong className="metric-value">{value ?? '—'}</strong><div className="metric-note"><i className={tone} />{note}</div></article>
}
function Status({ value }: { value: string }) { return <span className={`status status-${value.toLowerCase()}`}><i />{value.replace('_', ' ')}</span> }
function Empty({ loading }: { loading: boolean }) { return <div className="empty-state"><div className="empty-symbol"><BriefcaseBusiness size={20} /></div><strong>{loading ? 'Loading records...' : 'Nothing here yet'}</strong><span>{loading ? 'Syncing with the operations API.' : 'New requests will appear here as they arrive.'}</span></div> }

export default App
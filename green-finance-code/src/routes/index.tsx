import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import {
  LayoutDashboard, Building2, ShieldAlert, Leaf, Eye, Bell, FileText, Settings,
  Users, AlertTriangle, ShieldCheck, Sprout, Search, ChevronDown, Send,
  Car, FlaskConical, Zap, Droplets, Building, Pill, Heart, Cog, ShoppingCart, Cpu,
  Trophy, Award, BarChart3,
} from "lucide-react";
import { LineChart, Line, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export const Route = createFileRoute("/")({ component: Dashboard });

const spark = (seed: number, trend: "up" | "down" | "flat" = "flat") =>
  Array.from({ length: 12 }, (_, i) => ({
    v:
      50 +
      Math.sin(i + seed) * 8 +
      (trend === "up" ? i * 1.5 : trend === "down" ? -i * 1.2 : 0) +
      ((seed * 7) % 5),
  }));

const companies = [
  { sym: "TSLA", name: "Tesla Inc", price: 409.5, change: -3.02, risk: 80, green: 93.6, esg: "BB", sector: "Automobiles", icon: Car, trend: "down" as const },
  { sym: "ALB", name: "Albemarle Corp", price: 175.15, change: -2.9, risk: 60, green: 93.6, esg: "BB", sector: "Chemicals", icon: FlaskConical, trend: "down" as const },
  { sym: "XOM", name: "Exxon Mobil Corp", price: 160.02, change: 1.33, risk: 40, green: 10.0, esg: "CCC", sector: "Energy", icon: Zap, trend: "up" as const },
  { sym: "AES", name: "AES Corp", price: 14.51, change: 0.28, risk: 40, green: 25.0, esg: "B", sector: "Utilities", icon: Droplets, trend: "flat" as const },
  { sym: "ARE", name: "Alexandria Real Estate…", price: 46.54, change: 3.49, risk: 40, green: 87.1, esg: "BB", sector: "Real Estate", icon: Building, trend: "up" as const },
  { sym: "ABBV", name: "AbbVie Inc", price: 208.75, change: -0.78, risk: 40, green: 93.6, esg: "BB", sector: "Biotechnology", icon: Pill, trend: "down" as const },
  { sym: "ALGN", name: "Align Technology Inc", price: 159.18, change: 1.23, risk: 40, green: 93.6, esg: "BB", sector: "Health Care", icon: Heart, trend: "up" as const },
  { sym: "MMM", name: "3M Co", price: 152.13, change: 4.04, risk: 40, green: 93.6, esg: "BB", sector: "Industrial", icon: Cog, trend: "up" as const },
  { sym: "AMZN", name: "Amazon.com Inc", price: 264.52, change: 0.14, risk: 40, green: 93.6, esg: "BB", sector: "Retail", icon: ShoppingCart, trend: "flat" as const },
  { sym: "AMD", name: "Advanced Micro Devices…", price: 414.51, change: -2.26, risk: 40, green: 93.6, esg: "BB", sector: "Semiconductors", icon: Cpu, trend: "down" as const },
];

const sectorData = [
  { name: "Technology", value: 22, color: "oklch(0.62 0.16 155)" },
  { name: "Health Care", value: 18, color: "oklch(0.62 0.18 255)" },
  { name: "Financials", value: 15, color: "oklch(0.65 0.2 295)" },
  { name: "Industrials", value: 12, color: "oklch(0.72 0.16 50)" },
  { name: "Others", value: 33, color: "oklch(0.78 0.02 260)" },
];

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", active: true },
  { icon: Building2, label: "Companies" },
  { icon: ShieldAlert, label: "Risk Analytics" },
  { icon: Leaf, label: "ESG Scores" },
  { icon: Eye, label: "Watchlist" },
  { icon: Bell, label: "Alerts" },
  { icon: FileText, label: "Reports" },
  { icon: Settings, label: "Settings" },
];

function Sparkline({ data, color }: { data: { v: number }[]; color: string }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function KpiCard({
  icon: Icon, label, value, delta, deltaTone, iconBg, iconColor, sparkColor, sparkSeed, trend,
}: {
  icon: typeof Users; label: string; value: string; delta: string;
  deltaTone: "up" | "down"; iconBg: string; iconColor: string;
  sparkColor: string; sparkSeed: number; trend: "up" | "down";
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-start gap-4">
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${iconBg}`}>
          <Icon className={`h-5 w-5 ${iconColor}`} />
        </div>
        <div className="flex-1">
          <div className="text-xs font-medium text-muted-foreground">{label}</div>
          <div className="mt-1 text-3xl font-bold tracking-tight text-foreground">{value}</div>
        </div>
      </div>
      <div className="mt-3 flex items-end justify-between">
        <div className={`text-xs font-medium ${deltaTone === "up" ? "text-primary" : "text-destructive"}`}>
          {deltaTone === "up" ? "↑" : "↓"} {delta}
        </div>
        <div className="h-10 w-24">
          <Sparkline data={spark(sparkSeed, trend)} color={sparkColor} />
        </div>
      </div>
    </div>
  );
}

function Dashboard() {
  const [chat, setChat] = useState("");

  return (
    <div className="flex min-h-screen bg-background">
      {/* Sidebar */}
      <aside className="flex w-64 shrink-0 flex-col bg-sidebar text-sidebar-foreground">
        <div className="flex items-center gap-3 px-5 py-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/15">
            <Leaf className="h-5 w-5 text-primary" />
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold text-white">Green Finance</div>
            <div className="text-sm font-semibold text-white">Intelligence</div>
          </div>
        </div>

        <nav className="mt-2 flex-1 space-y-1 px-3">
          {navItems.map((it) => (
            <button
              key={it.label}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                it.active
                  ? "bg-primary text-primary-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent"
              }`}
            >
              <it.icon className="h-4 w-4" />
              {it.label}
            </button>
          ))}
        </nav>

        <div className="m-3 rounded-xl bg-sidebar-accent/60 p-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary/30 text-xs font-semibold text-white">
              AK
            </div>
            <div className="flex-1 leading-tight">
              <div className="text-sm font-medium text-white">Arben K.</div>
              <div className="text-[11px] text-sidebar-foreground/70">Senior Solution Developer</div>
            </div>
            <ChevronDown className="h-4 w-4 text-sidebar-foreground/70" />
          </div>
        </div>

        <div className="mx-3 mb-4 rounded-xl border border-sidebar-border bg-sidebar-accent/40 p-3">
          <div className="text-xs text-sidebar-foreground/70">Market Overview</div>
          <div className="mt-1 text-xs font-medium text-sidebar-foreground">S&P 500</div>
          <div className="mt-2 h-10">
            <Sparkline data={spark(3, "up")} color="oklch(0.72 0.17 158)" />
          </div>
          <div className="mt-2 flex items-end justify-between">
            <div className="text-base font-semibold text-white">5,309.01</div>
            <div className="text-xs font-medium text-primary">+0.78%</div>
          </div>
          <div className="mt-2 text-[10px] text-sidebar-foreground/60">Last updated: just now</div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-x-hidden">
        {/* Header */}
        <header className="flex items-center justify-between px-8 pt-7 pb-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Welcome back, Arben! <span className="ml-1">👋</span>
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Here's what's happening with your green finance portfolio today.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                placeholder="Search companies, sectors..."
                className="w-72 rounded-full border border-border bg-card py-2 pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <button className="rounded-full border border-border bg-card p-2 text-muted-foreground hover:text-foreground">
              <Bell className="h-4 w-4" />
            </button>
            <div className="flex items-center gap-2 rounded-full bg-accent px-3 py-1.5 text-xs font-medium text-accent-foreground">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
              </span>
              Live · 27 companies
            </div>
          </div>
        </header>

        {/* KPIs */}
        <section className="grid grid-cols-1 gap-5 px-8 md:grid-cols-2 xl:grid-cols-4">
          <KpiCard icon={Users} label="Companies Tracked" value="27"
            delta="3 new this week" deltaTone="up"
            iconBg="bg-accent" iconColor="text-primary"
            sparkColor="oklch(0.62 0.16 155)" sparkSeed={1} trend="up" />
          <KpiCard icon={AlertTriangle} label="High Risk Companies" value="2"
            delta="-1 from yesterday" deltaTone="down"
            iconBg="bg-destructive/10" iconColor="text-destructive"
            sparkColor="oklch(0.62 0.22 25)" sparkSeed={2} trend="down" />
          <KpiCard icon={ShieldCheck} label="Low Risk Companies" value="13"
            delta="2 from yesterday" deltaTone="up"
            iconBg="bg-info/10" iconColor="text-[oklch(0.62_0.18_255)]"
            sparkColor="oklch(0.62 0.18 255)" sparkSeed={4} trend="up" />
          <KpiCard icon={Sprout} label="Avg Green Score" value="86.1"
            delta="4.3 vs last week" deltaTone="up"
            iconBg="bg-accent" iconColor="text-primary"
            sparkColor="oklch(0.62 0.16 155)" sparkSeed={6} trend="up" />
        </section>

        {/* Content */}
        <section className="grid grid-cols-1 gap-5 px-8 py-5 xl:grid-cols-[2fr_1fr]">
          {/* Left: company table */}
          <div className="rounded-2xl border border-border bg-card shadow-sm">
            <div className="flex items-center justify-between border-b border-border px-6 py-4">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-primary" />
                <h2 className="text-sm font-semibold text-foreground">Live Company Scores</h2>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  Auto-refresh: 60s
                </div>
                <button className="rounded-full border border-border px-3 py-1 text-xs font-medium text-foreground hover:bg-muted">
                  View all
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    {["Symbol", "Company", "Price", "Change", "Risk Score", "Green Score", "ESG", "Sector", "Trend"].map((h) => (
                      <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {companies.map((c) => {
                    const riskColor = c.risk >= 60 ? "bg-destructive" : c.risk >= 40 ? "bg-[oklch(0.78_0.16_75)]" : "bg-primary";
                    const trendColor = c.trend === "up" ? "oklch(0.62 0.16 155)" : c.trend === "down" ? "oklch(0.62 0.22 25)" : "oklch(0.65 0.04 260)";
                    return (
                      <tr key={c.sym} className="border-t border-border/60 hover:bg-muted/40">
                        <td className="px-4 py-3 font-semibold text-foreground">{c.sym}</td>
                        <td className="px-4 py-3 text-foreground">{c.name}</td>
                        <td className="px-4 py-3 text-foreground">${c.price.toFixed(2)}</td>
                        <td className={`px-4 py-3 font-medium ${c.change >= 0 ? "text-primary" : "text-destructive"}`}>
                          {c.change >= 0 ? "+" : ""}{c.change.toFixed(2)}%
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className={`h-2.5 w-2.5 rounded-full ${riskColor}`} />
                            <span className="text-foreground">{c.risk}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1.5">
                            <Leaf className="h-3.5 w-3.5 text-primary" />
                            <span className="text-foreground">{c.green.toFixed(1)}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-foreground">{c.esg}</td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <c.icon className="h-4 w-4" />
                            <span>{c.sector}</span>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="h-8 w-20">
                            <Sparkline data={spark(c.sym.length, c.trend === "flat" ? "up" : c.trend)} color={trendColor} />
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-center gap-1 border-t border-border px-6 py-3 text-xs font-medium text-muted-foreground hover:text-foreground cursor-pointer">
              View more companies <ChevronDown className="h-3.5 w-3.5" />
            </div>
          </div>

          {/* Right: AI + Sector */}
          <div className="space-y-5">
            {/* AI Assistant */}
            <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-foreground">AI Assistant</h3>
                    <span className="rounded-full bg-accent px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-accent-foreground">
                      Beta
                    </span>
                  </div>
                  <p className="mt-0.5 text-[11px] text-muted-foreground">
                    Powered by real-time BigQuery data
                  </p>
                </div>
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-[oklch(0.72_0.17_158)] text-xl">
                  🤖
                </div>
              </div>

              <div className="mt-4 rounded-xl bg-muted/60 p-3 text-xs leading-relaxed text-foreground">
                Hello! I analyze S&P 500 companies using real-time data from BigQuery. Ask me about
                risks, green scores, or investment recommendations!
              </div>

              <form
                onSubmit={(e) => { e.preventDefault(); setChat(""); }}
                className="mt-3 flex items-center gap-2 rounded-full bg-primary p-1 pl-4"
              >
                <input
                  value={chat}
                  onChange={(e) => setChat(e.target.value)}
                  placeholder="Ask me anything..."
                  className="flex-1 bg-transparent text-xs text-primary-foreground placeholder:text-primary-foreground/70 focus:outline-none"
                />
                <button type="submit" className="flex h-7 w-7 items-center justify-center rounded-full bg-white/20 text-primary-foreground hover:bg-white/30">
                  <Send className="h-3.5 w-3.5" />
                </button>
              </form>
            </div>

            {/* Quick Analysis */}
            <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
              <h4 className="text-sm font-semibold text-foreground">Quick Analysis</h4>
              <div className="mt-3 grid grid-cols-2 gap-2">
                {[
                  { icon: Trophy, label: "Best Investment" },
                  { icon: Leaf, label: "ESG Leaders" },
                  { icon: BarChart3, label: "Risk Comparison" },
                  { icon: Award, label: "Companies to Watch" },
                ].map((q) => (
                  <button key={q.label} className="flex items-center gap-2 rounded-lg border border-border bg-muted/50 px-3 py-2 text-xs font-medium text-foreground transition-colors hover:bg-accent hover:text-accent-foreground">
                    <q.icon className="h-3.5 w-3.5 text-primary" />
                    {q.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sector breakdown */}
            <div className="rounded-2xl border border-border bg-card p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-foreground">Sector Breakdown</h4>
                <button className="text-xs font-medium text-muted-foreground hover:text-foreground">View all</button>
              </div>
              <div className="mt-2 flex items-center gap-4">
                <div className="relative h-32 w-32 shrink-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={sectorData} dataKey="value" innerRadius={38} outerRadius={58} paddingAngle={2} stroke="none">
                        {sectorData.map((s, i) => <Cell key={i} fill={s.color} />)}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-xl font-bold text-foreground">27</div>
                    <div className="text-[10px] text-muted-foreground">Total</div>
                  </div>
                </div>
                <ul className="flex-1 space-y-1.5 text-xs">
                  {sectorData.map((s) => (
                    <li key={s.name} className="flex items-center justify-between">
                      <span className="flex items-center gap-2 text-foreground">
                        <span className="h-2 w-2 rounded-full" style={{ background: s.color }} />
                        {s.name}
                      </span>
                      <span className="font-medium text-muted-foreground">{s.value}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Recent Alerts */}
        <section className="px-8 pb-8">
          <div className="rounded-2xl border border-border bg-card shadow-sm">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4 text-foreground" />
                <h3 className="text-sm font-semibold text-foreground">Recent Alerts</h3>
              </div>
              <button className="text-xs font-medium text-primary hover:underline">View all alerts →</button>
            </div>
            <div className="grid grid-cols-1 gap-3 px-6 pb-5 md:grid-cols-3">
              {[
                { icon: AlertTriangle, iconBg: "bg-destructive/10", iconColor: "text-destructive", title: "High risk score alert", desc: "Tesla Inc (TSLA) risk score increased to 80", time: "2m ago" },
                { icon: Leaf, iconBg: "bg-accent", iconColor: "text-primary", title: "ESG improvement", desc: "Amazon.com Inc (AMZN) improved ESG score", time: "15m ago" },
                { icon: ShieldCheck, iconBg: "bg-info/10", iconColor: "text-[oklch(0.62_0.18_255)]", title: "New company added", desc: "NVIDIA Corporation added to tracking", time: "1h ago" },
              ].map((a) => (
                <div key={a.title} className="flex gap-3 rounded-xl border border-border bg-muted/40 p-4">
                  <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${a.iconBg}`}>
                    <a.icon className={`h-4 w-4 ${a.iconColor}`} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-xs font-semibold text-foreground">{a.title}</div>
                    <div className="mt-0.5 text-[11px] leading-relaxed text-muted-foreground">{a.desc}</div>
                    <div className="mt-1.5 text-[10px] text-muted-foreground/80">{a.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FiTrendingUp, FiClock, FiBarChart2, FiMessageCircle, FiThumbsUp, FiZap } from 'react-icons/fi'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const API = 'http://localhost:8000'

const COLORS = ['#6366f1', '#a855f7', '#22c55e', '#f97316', '#ec4899', '#eab308', '#14b8a6', '#ef4444']

function StatCard({ icon: Icon, label, value, trend, color = 'brand' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-4"
    >
      <div className="flex items-center justify-between mb-2">
        <Icon size={18} className={`text-${color}-400`} />
        {trend !== undefined && (
          <span className={`text-xs font-medium ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-slate-100">{value}</p>
      <p className="text-xs text-slate-500 mt-0.5">{label}</p>
    </motion.div>
  )
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-card px-3 py-2 text-xs">
      <p className="text-slate-300 font-medium">{label}</p>
      <p className="text-brand-400">{payload[0]?.value}</p>
    </div>
  )
}

export default function AnalyticsDashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true)
      try {
        const res = await fetch(`${API}/api/analytics?days=${days}`)
        if (res.ok) {
          setData(await res.json())
        }
      } catch {
        // Generate sample data for demo
        setData(generateSampleData())
      } finally {
        setLoading(false)
      }
    }
    fetchAnalytics()
  }, [days])

  if (loading) {
    return (
      <div className="space-y-4 p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[1,2,3,4].map(i => <div key={i} className="glass-card p-4"><div className="skeleton h-6 w-1/2 mb-2" /><div className="skeleton h-4 w-3/4" /></div>)}
        </div>
      </div>
    )
  }

  const categoryData = Object.entries(data?.questions_by_category || {}).map(([name, value]) => ({ name, value }))
  const timelineData = (data?.questions_over_time || []).map(d => ({ ...d, date: d.date?.slice(5) }))
  const peakData = (data?.peak_hours || []).map(d => ({ ...d, hour: `${d.hour}:00` }))

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100">Analytics Dashboard</h2>
          <p className="text-sm text-slate-400">Usage insights and trends</p>
        </div>
        <div className="flex gap-2">
          {[7, 30, 90].map(d => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                days === d
                  ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                  : 'text-slate-400 hover:text-slate-300 bg-surface-800/50'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon={FiMessageCircle} label="Total Questions" value={data?.total_questions || 0} color="brand" />
        <StatCard icon={FiZap} label="Avg Response" value={`${data?.avg_response_time || 0}s`} color="purple" />
        <StatCard icon={FiBarChart2} label="Avg Confidence" value={`${Math.round(data?.avg_confidence || 0)}%`} color="green" />
        <StatCard icon={FiThumbsUp} label="Satisfaction" value={`${data?.satisfaction_rating || 0}/5`} color="yellow" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Timeline */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4">
          <h4 className="text-sm font-semibold text-slate-200 mb-4">Questions Over Time</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={timelineData}>
              <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Categories */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card p-4">
          <h4 className="text-sm font-semibold text-slate-200 mb-4">By Category</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={categoryData}>
              <XAxis dataKey="name" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Peak Hours */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-4">
          <h4 className="text-sm font-semibold text-slate-200 mb-4">Peak Hours</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={peakData}>
              <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#64748b', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="count" fill="#a855f7" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Trending */}
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-4">
          <h4 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
            <FiTrendingUp className="text-orange-400" /> Trending Questions
          </h4>
          <div className="space-y-2">
            {(data?.trending_questions || []).slice(0, 5).map((q, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="text-slate-500 text-xs w-5">{i + 1}.</span>
                <span className="text-slate-300 text-xs flex-1 truncate">{q.query}</span>
                <span className="text-xs text-slate-500">{q.count}×</span>
                {q.trending && <FiTrendingUp size={12} className="text-green-400" />}
              </div>
            ))}
            {(!data?.trending_questions || data.trending_questions.length === 0) && (
              <p className="text-xs text-slate-500 text-center py-4">No trending data yet. Start asking questions!</p>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function generateSampleData() {
  const categories = ['grading', 'attendance', 'exam', 'financial', 'withdrawal', 'integrity']
  const questionsByCategory = {}
  categories.forEach(c => { questionsByCategory[c] = Math.floor(Math.random() * 50) + 5 })

  const questionsOverTime = []
  for (let i = 29; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    questionsOverTime.push({ date: d.toISOString().slice(0, 10), count: Math.floor(Math.random() * 20) + 1 })
  }

  const peakHours = []
  for (let h = 8; h <= 22; h++) {
    peakHours.push({ hour: h, count: Math.floor(Math.random() * 30) + 2 })
  }

  return {
    total_questions: 247,
    avg_response_time: 1.8,
    avg_confidence: 78.5,
    satisfaction_rating: 4.2,
    questions_by_category: questionsByCategory,
    questions_over_time: questionsOverTime,
    peak_hours: peakHours,
    trending_questions: [
      { query: 'What GPA do I need for good standing?', count: 34, trending: true },
      { query: 'How many absences are allowed?', count: 28, trending: true },
      { query: 'How do I withdraw from a course?', count: 22, trending: false },
      { query: 'What is the plagiarism policy?', count: 18, trending: true },
      { query: 'When is the scholarship deadline?', count: 15, trending: false },
    ],
    top_policies: [],
  }
}

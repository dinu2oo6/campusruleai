import { useState } from 'react'
import { motion } from 'framer-motion'
import { FiSettings, FiMoon, FiSun, FiType, FiGlobe, FiBookOpen } from 'react-icons/fi'
import useTheme from '../hooks/useTheme'
import useLocalStorage from '../hooks/useLocalStorage'
import PolicyComparison from '../components/PolicyComparison'
import Calculator from '../components/Calculator'
import PolicyGraph from '../components/PolicyGraph'

export default function Settings() {
  const { theme, setTheme } = useTheme()
  const [fontSize, setFontSize] = useLocalStorage('campusrule-fontsize', 'normal')
  const [responseStyle, setResponseStyle] = useLocalStorage('campusrule-response-style', 'detailed')
  const [activeSection, setActiveSection] = useState('preferences')

  const sections = [
    { id: 'preferences', label: '⚙️ Preferences', icon: FiSettings },
    { id: 'comparison', label: '⚖️ Compare Policies', icon: FiBookOpen },
    { id: 'calculator', label: '🧮 Calculators', icon: FiBookOpen },
    { id: 'graph', label: '🕸️ Knowledge Graph', icon: FiBookOpen },
  ]

  return (
    <div className="flex-1 overflow-y-auto px-6 py-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FiSettings className="text-brand-400" /> Settings & Tools
          </h2>
          <p className="text-sm text-slate-400 mt-1">Customize your experience and explore interactive tools</p>
        </div>

        {/* Section tabs */}
        <div className="flex flex-wrap gap-2">
          {sections.map(s => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeSection === s.id
                  ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                  : 'text-slate-400 hover:text-slate-300 bg-surface-800/50 border border-surface-600/40'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>

        {/* Preferences */}
        {activeSection === 'preferences' && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {/* Theme */}
            <div className="glass-card p-5">
              <h4 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <FiMoon className="text-brand-400" /> Appearance
              </h4>
              <div className="flex gap-3">
                {['dark', 'light', 'auto'].map(t => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={`flex-1 p-3 rounded-xl border text-center transition-all ${
                      theme === t || (t === 'auto' && false)
                        ? 'border-brand-500/40 bg-brand-500/10'
                        : 'border-surface-600/40 hover:border-surface-500/50'
                    }`}
                  >
                    {t === 'dark' && <FiMoon className="mx-auto mb-1 text-purple-400" />}
                    {t === 'light' && <FiSun className="mx-auto mb-1 text-yellow-400" />}
                    {t === 'auto' && <FiGlobe className="mx-auto mb-1 text-blue-400" />}
                    <p className="text-xs text-slate-300 capitalize">{t}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Font size */}
            <div className="glass-card p-5">
              <h4 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <FiType className="text-brand-400" /> Font Size
              </h4>
              <div className="flex gap-3">
                {[
                  { id: 'small', label: 'A-', size: 'text-xs' },
                  { id: 'normal', label: 'A', size: 'text-sm' },
                  { id: 'large', label: 'A+', size: 'text-lg' },
                ].map(opt => (
                  <button
                    key={opt.id}
                    onClick={() => setFontSize(opt.id)}
                    className={`flex-1 p-3 rounded-xl border text-center transition-all ${
                      fontSize === opt.id
                        ? 'border-brand-500/40 bg-brand-500/10'
                        : 'border-surface-600/40 hover:border-surface-500/50'
                    }`}
                  >
                    <span className={`${opt.size} text-slate-200 font-medium`}>{opt.label}</span>
                    <p className="text-[10px] text-slate-500 mt-1 capitalize">{opt.id}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Response style */}
            <div className="glass-card p-5">
              <h4 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <FiBookOpen className="text-brand-400" /> Response Style
              </h4>
              <div className="flex gap-3">
                {[
                  { id: 'concise', label: 'Concise', desc: 'Brief, to-the-point answers' },
                  { id: 'detailed', label: 'Detailed', desc: 'Full explanations with context' },
                ].map(opt => (
                  <button
                    key={opt.id}
                    onClick={() => setResponseStyle(opt.id)}
                    className={`flex-1 p-3 rounded-xl border text-left transition-all ${
                      responseStyle === opt.id
                        ? 'border-brand-500/40 bg-brand-500/10'
                        : 'border-surface-600/40 hover:border-surface-500/50'
                    }`}
                  >
                    <p className="text-xs text-slate-200 font-medium">{opt.label}</p>
                    <p className="text-[10px] text-slate-500 mt-0.5">{opt.desc}</p>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Policy Comparison */}
        {activeSection === 'comparison' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <PolicyComparison />
          </motion.div>
        )}

        {/* Calculators */}
        {activeSection === 'calculator' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <Calculator />
          </motion.div>
        )}

        {/* Knowledge Graph */}
        {activeSection === 'graph' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <PolicyGraph />
          </motion.div>
        )}
      </div>
    </div>
  )
}

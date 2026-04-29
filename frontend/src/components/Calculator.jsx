import { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { FiHash, FiAward, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi'

function GPACalculator() {
  const [currentGPA, setCurrentGPA] = useState('')
  const [totalCredits, setTotalCredits] = useState('')
  const [courseGrade, setCourseGrade] = useState('A')
  const [courseCredits, setCourseCredits] = useState('3')

  const gradePoints = {
    'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
    'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0,
  }

  const result = useMemo(() => {
    const gpa = parseFloat(currentGPA)
    const credits = parseFloat(totalCredits)
    const newCredits = parseFloat(courseCredits)
    const gradeVal = gradePoints[courseGrade]

    if (isNaN(gpa) || isNaN(credits) || isNaN(newCredits) || credits <= 0) return null

    const currentQP = gpa * credits
    const newQP = gradeVal * newCredits
    const newGPA = (currentQP + newQP) / (credits + newCredits)

    return {
      newGPA: Math.round(newGPA * 1000) / 1000,
      deanslist: newGPA >= 3.5,
      probation: newGPA < 1.75,
      goodStanding: newGPA >= 2.0,
      change: Math.round((newGPA - gpa) * 1000) / 1000,
    }
  }, [currentGPA, totalCredits, courseGrade, courseCredits])

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Current GPA</label>
          <input
            type="number" step="0.01" min="0" max="4"
            value={currentGPA} onChange={e => setCurrentGPA(e.target.value)}
            placeholder="3.25"
            className="w-full bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Total Credits</label>
          <input
            type="number" min="1"
            value={totalCredits} onChange={e => setTotalCredits(e.target.value)}
            placeholder="60"
            className="w-full bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">New Course Grade</label>
          <select
            value={courseGrade} onChange={e => setCourseGrade(e.target.value)}
            className="w-full bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
          >
            {Object.keys(gradePoints).map(g => <option key={g} value={g}>{g} ({gradePoints[g]})</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Course Credits</label>
          <input
            type="number" min="1" max="6"
            value={courseCredits} onChange={e => setCourseCredits(e.target.value)}
            className="w-full bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
          />
        </div>
      </div>

      {result && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-4 space-y-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">New GPA</span>
            <span className="text-2xl font-bold text-slate-100">{result.newGPA.toFixed(3)}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium ${result.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {result.change >= 0 ? '↑' : '↓'} {Math.abs(result.change).toFixed(3)}
            </span>
            <span className="text-slate-500 text-xs">change</span>
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2">
            <div className={`text-center p-2 rounded-lg ${result.deanslist ? 'bg-green-500/10 border border-green-500/20' : 'bg-surface-700/30'}`}>
              <FiAward size={14} className={result.deanslist ? 'text-green-400 mx-auto mb-1' : 'text-slate-600 mx-auto mb-1'} />
              <p className="text-[10px] text-slate-400">Dean's List</p>
              <p className={`text-xs font-bold ${result.deanslist ? 'text-green-400' : 'text-slate-600'}`}>
                {result.deanslist ? 'Yes ✓' : 'No'}
              </p>
            </div>
            <div className={`text-center p-2 rounded-lg ${result.goodStanding ? 'bg-blue-500/10 border border-blue-500/20' : 'bg-yellow-500/10 border border-yellow-500/20'}`}>
              <FiCheckCircle size={14} className={result.goodStanding ? 'text-blue-400 mx-auto mb-1' : 'text-yellow-400 mx-auto mb-1'} />
              <p className="text-[10px] text-slate-400">Standing</p>
              <p className={`text-xs font-bold ${result.goodStanding ? 'text-blue-400' : 'text-yellow-400'}`}>
                {result.goodStanding ? 'Good' : 'Warning'}
              </p>
            </div>
            <div className={`text-center p-2 rounded-lg ${result.probation ? 'bg-red-500/10 border border-red-500/20' : 'bg-surface-700/30'}`}>
              <FiAlertTriangle size={14} className={result.probation ? 'text-red-400 mx-auto mb-1' : 'text-slate-600 mx-auto mb-1'} />
              <p className="text-[10px] text-slate-400">Probation</p>
              <p className={`text-xs font-bold ${result.probation ? 'text-red-400' : 'text-slate-600'}`}>
                {result.probation ? 'At Risk!' : 'No'}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

function GraduationCalculator() {
  const [currentCredits, setCurrentCredits] = useState('')
  const [creditsPerSem, setCreditsPerSem] = useState('15')
  const requiredCredits = 120

  const result = useMemo(() => {
    const current = parseInt(currentCredits)
    const perSem = parseInt(creditsPerSem)
    if (isNaN(current) || isNaN(perSem) || perSem <= 0) return null

    const remaining = Math.max(requiredCredits - current, 0)
    const semesters = Math.ceil(remaining / perSem)
    const years = (semesters / 2).toFixed(1)

    return { remaining, semesters, years, progress: Math.round((current / requiredCredits) * 100) }
  }, [currentCredits, creditsPerSem])

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Credits Completed</label>
          <input
            type="number" min="0" max="200"
            value={currentCredits} onChange={e => setCurrentCredits(e.target.value)}
            placeholder="60"
            className="w-full bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
          />
        </div>
        <div>
          <label className="text-xs text-slate-400 mb-1 block">Credits / Semester</label>
          <input
            type="number" min="1" max="21"
            value={creditsPerSem} onChange={e => setCreditsPerSem(e.target.value)}
            className="w-full bg-surface-800/50 border border-surface-600/40 rounded-lg px-3 py-2 text-sm text-slate-200 outline-none focus:border-brand-500"
          />
        </div>
      </div>

      {result && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-sm">Progress</span>
            <span className="text-lg font-bold text-slate-100">{result.progress}%</span>
          </div>
          <div className="confidence-bar h-2">
            <motion.div
              className="confidence-fill bg-gradient-to-r from-brand-500 to-purple-500"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(result.progress, 100)}%` }}
              transition={{ duration: 0.8 }}
            />
          </div>
          <div className="grid grid-cols-3 gap-3 text-center pt-1">
            <div>
              <p className="text-lg font-bold text-brand-400">{result.remaining}</p>
              <p className="text-[10px] text-slate-500">Credits Left</p>
            </div>
            <div>
              <p className="text-lg font-bold text-purple-400">{result.semesters}</p>
              <p className="text-[10px] text-slate-500">Semesters</p>
            </div>
            <div>
              <p className="text-lg font-bold text-neon-blue">{result.years}</p>
              <p className="text-[10px] text-slate-500">Years</p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default function Calculator() {
  const [activeCalc, setActiveCalc] = useState('gpa')

  const calcs = [
    { id: 'gpa', label: '🎓 GPA Impact', component: <GPACalculator /> },
    { id: 'graduation', label: '🎓 Graduation', component: <GraduationCalculator /> },
  ]

  return (
    <div className="space-y-4">
      <div className="text-center mb-4">
        <h3 className="text-lg font-bold text-slate-100 mb-1 flex items-center justify-center gap-2">
          <FiHash className="text-brand-400" /> Calculators
        </h3>
        <p className="text-slate-400 text-sm">Interactive tools using policy data</p>
      </div>

      <div className="flex gap-2 justify-center">
        {calcs.map(c => (
          <button
            key={c.id}
            onClick={() => setActiveCalc(c.id)}
            className={`px-4 py-2 rounded-xl text-xs font-medium transition-all ${
              activeCalc === c.id
                ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                : 'text-slate-400 hover:text-slate-300 bg-surface-800/50 border border-surface-600/40'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      <div className="glass-card p-4">
        {calcs.find(c => c.id === activeCalc)?.component}
      </div>
    </div>
  )
}

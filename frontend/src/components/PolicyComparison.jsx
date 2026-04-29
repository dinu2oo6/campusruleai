import { motion } from 'framer-motion'

const COMPARISONS = {
  'withdrawal_vs_drop': {
    title: 'Withdrawal vs Drop',
    left: { name: 'Withdrawal', items: [
      { label: 'Deadline', value: '80% of term', favorable: false },
      { label: 'Transcript', value: 'Shows "W"', favorable: false },
      { label: 'Refund', value: 'None / Partial', favorable: false },
      { label: 'GPA Impact', value: 'No impact', favorable: true },
      { label: 'Financial Aid', value: 'May affect', favorable: false },
      { label: 'Max per term', value: 'No limit', favorable: true },
    ]},
    right: { name: 'Drop', items: [
      { label: 'Deadline', value: '100% refund period', favorable: true },
      { label: 'Transcript', value: 'No record', favorable: true },
      { label: 'Refund', value: 'Full refund', favorable: true },
      { label: 'GPA Impact', value: 'No impact', favorable: true },
      { label: 'Financial Aid', value: 'Adjusted', favorable: true },
      { label: 'Max per term', value: 'No limit', favorable: true },
    ]},
  },
  'probation_vs_suspension': {
    title: 'Probation vs Suspension',
    left: { name: 'Probation', items: [
      { label: 'GPA Threshold', value: 'Below 1.75', favorable: false },
      { label: 'Can Enroll', value: 'Yes, with plan', favorable: true },
      { label: 'Duration', value: '1 semester', favorable: true },
      { label: 'Recovery', value: 'Raise GPA to 2.0', favorable: true },
      { label: 'Advisor Meeting', value: 'Required', favorable: false },
      { label: 'Course Load', value: 'May be limited', favorable: false },
    ]},
    right: { name: 'Suspension', items: [
      { label: 'GPA Threshold', value: '2nd sem below 1.75', favorable: false },
      { label: 'Can Enroll', value: 'No - 1 year out', favorable: false },
      { label: 'Duration', value: '1 academic year', favorable: false },
      { label: 'Recovery', value: 'Reapply for admission', favorable: false },
      { label: 'Advisor Meeting', value: 'Required on return', favorable: false },
      { label: 'Course Load', value: 'Limited on return', favorable: false },
    ]},
  },
  'excused_vs_unexcused': {
    title: 'Excused vs Unexcused Absence',
    left: { name: 'Excused', items: [
      { label: 'Documentation', value: 'Required', favorable: false },
      { label: 'Grade Impact', value: 'None', favorable: true },
      { label: 'Makeup Work', value: 'Allowed', favorable: true },
      { label: 'Limit', value: 'No limit', favorable: true },
      { label: 'Notification', value: 'Within 72 hours', favorable: false },
      { label: 'Examples', value: 'Medical, family', favorable: true },
    ]},
    right: { name: 'Unexcused', items: [
      { label: 'Documentation', value: 'Not applicable', favorable: true },
      { label: 'Grade Impact', value: 'Grade reduction', favorable: false },
      { label: 'Makeup Work', value: 'Not guaranteed', favorable: false },
      { label: 'Limit', value: 'Max 3 per course', favorable: false },
      { label: 'Notification', value: 'Not required', favorable: true },
      { label: 'Examples', value: 'Oversleeping, etc.', favorable: false },
    ]},
  },
}

export default function PolicyComparison() {
  const comparisonKeys = Object.keys(COMPARISONS)

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <h3 className="text-lg font-bold text-slate-100 mb-1">Policy Comparisons</h3>
        <p className="text-slate-400 text-sm">Side-by-side comparison of similar policies</p>
      </div>

      {comparisonKeys.map((key, idx) => {
        const comp = COMPARISONS[key]
        return (
          <motion.div
            key={key}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="glass-card overflow-hidden"
          >
            <div className="px-4 py-3 border-b border-surface-600/30 bg-surface-800/50">
              <h4 className="text-sm font-semibold text-slate-200">{comp.title}</h4>
            </div>

            <div className="grid grid-cols-2 divide-x divide-surface-600/30">
              {/* Headers */}
              <div className="px-4 py-2 bg-brand-500/5 text-center">
                <span className="text-xs font-bold text-brand-400">{comp.left.name}</span>
              </div>
              <div className="px-4 py-2 bg-purple-500/5 text-center">
                <span className="text-xs font-bold text-purple-400">{comp.right.name}</span>
              </div>

              {/* Rows */}
              {comp.left.items.map((leftItem, i) => {
                const rightItem = comp.right.items[i]
                return (
                  <ComparisonRow key={i} left={leftItem} right={rightItem} isLast={i === comp.left.items.length - 1} />
                )
              })}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}

function ComparisonRow({ left, right, isLast }) {
  return (
    <>
      <div className={`px-4 py-2.5 ${!isLast ? 'border-b border-surface-600/20' : ''}`}>
        <p className="text-[10px] text-slate-500 mb-0.5">{left.label}</p>
        <p className={`text-xs font-medium ${left.favorable ? 'text-green-400' : 'text-red-400'}`}>
          {left.favorable ? '🟢' : '🔴'} {left.value}
        </p>
      </div>
      <div className={`px-4 py-2.5 ${!isLast ? 'border-b border-surface-600/20' : ''}`}>
        <p className="text-[10px] text-slate-500 mb-0.5">{right.label}</p>
        <p className={`text-xs font-medium ${right.favorable ? 'text-green-400' : 'text-red-400'}`}>
          {right.favorable ? '🟢' : '🔴'} {right.value}
        </p>
      </div>
    </>
  )
}

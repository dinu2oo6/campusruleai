import { motion } from 'framer-motion'
import { FiSun, FiMoon } from 'react-icons/fi'

export default function ThemeToggle({ theme, onToggle }) {
  return (
    <motion.button
      whileTap={{ scale: 0.92 }}
      onClick={onToggle}
      className="relative p-2 rounded-xl bg-surface-800/50 border border-surface-600/40 hover:border-brand-500/30 transition-all"
      title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <motion.div
        initial={false}
        animate={{ rotate: theme === 'dark' ? 0 : 180 }}
        transition={{ duration: 0.3 }}
      >
        {theme === 'dark'
          ? <FiMoon size={16} className="text-slate-400" />
          : <FiSun size={16} className="text-yellow-400" />
        }
      </motion.div>
    </motion.button>
  )
}

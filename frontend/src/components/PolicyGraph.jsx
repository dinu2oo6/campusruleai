import { useState, useEffect, useRef, useCallback } from 'react'
import { motion } from 'framer-motion'

const NODES = [
  { id: 'grading', label: 'Grading Policy', category: 'grading', x: 400, y: 100 },
  { id: 'gpa', label: 'GPA Calculation', category: 'grading', x: 600, y: 60 },
  { id: 'standing', label: 'Academic Standing', category: 'grading', x: 800, y: 100 },
  { id: 'appeals', label: 'Grade Appeals', category: 'grading', x: 400, y: 220 },
  { id: 'deanslist', label: "Dean's List", category: 'grading', x: 600, y: 200 },
  { id: 'probation', label: 'Probation', category: 'grading', x: 800, y: 220 },
  { id: 'attendance', label: 'Attendance', category: 'attendance', x: 200, y: 180 },
  { id: 'absences', label: 'Excused Absences', category: 'attendance', x: 100, y: 300 },
  { id: 'integrity', label: 'Academic Integrity', category: 'integrity', x: 500, y: 340 },
  { id: 'plagiarism', label: 'Plagiarism', category: 'integrity', x: 400, y: 430 },
  { id: 'conduct', label: 'Code of Conduct', category: 'disciplinary', x: 650, y: 400 },
  { id: 'withdrawal', label: 'Withdrawal', category: 'withdrawal', x: 200, y: 400 },
  { id: 'refund', label: 'Tuition Refund', category: 'financial', x: 100, y: 500 },
  { id: 'financial', label: 'Financial Aid', category: 'financial', x: 300, y: 500 },
  { id: 'exams', label: 'Final Exams', category: 'exam', x: 700, y: 300 },
  { id: 'makeup', label: 'Makeup Exams', category: 'exam', x: 850, y: 350 },
  { id: 'prereqs', label: 'Prerequisites', category: 'prerequisites', x: 900, y: 460 },
]

const EDGES = [
  { from: 'grading', to: 'gpa' },
  { from: 'gpa', to: 'standing' },
  { from: 'grading', to: 'appeals' },
  { from: 'gpa', to: 'deanslist' },
  { from: 'standing', to: 'probation' },
  { from: 'attendance', to: 'grading' },
  { from: 'attendance', to: 'absences' },
  { from: 'integrity', to: 'plagiarism' },
  { from: 'integrity', to: 'conduct' },
  { from: 'withdrawal', to: 'refund' },
  { from: 'withdrawal', to: 'financial' },
  { from: 'exams', to: 'makeup' },
  { from: 'exams', to: 'integrity' },
  { from: 'standing', to: 'financial' },
  { from: 'prereqs', to: 'grading' },
  { from: 'withdrawal', to: 'standing' },
]

const CATEGORY_COLORS = {
  grading: '#3b82f6',
  attendance: '#22c55e',
  exam: '#a855f7',
  disciplinary: '#ef4444',
  integrity: '#f97316',
  financial: '#eab308',
  prerequisites: '#14b8a6',
  withdrawal: '#ec4899',
}

export default function PolicyGraph() {
  const canvasRef = useRef(null)
  const [hoveredNode, setHoveredNode] = useState(null)
  const [dragNode, setDragNode] = useState(null)
  const [nodes, setNodes] = useState(NODES)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const animRef = useRef(null)

  const drawGraph = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1

    canvas.width = canvas.offsetWidth * dpr
    canvas.height = canvas.offsetHeight * dpr
    ctx.scale(dpr, dpr)
    ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)

    const w = canvas.offsetWidth
    const h = canvas.offsetHeight

    // Draw edges
    for (const edge of EDGES) {
      const from = nodes.find(n => n.id === edge.from)
      const to = nodes.find(n => n.id === edge.to)
      if (!from || !to) continue

      const fx = (from.x / 1000) * w
      const fy = (from.y / 600) * h
      const tx = (to.x / 1000) * w
      const ty = (to.y / 600) * h

      ctx.beginPath()
      ctx.moveTo(fx, fy)
      ctx.lineTo(tx, ty)

      const isHovered = hoveredNode === edge.from || hoveredNode === edge.to
      ctx.strokeStyle = isHovered ? 'rgba(99,102,241,0.6)' : 'rgba(51,65,85,0.4)'
      ctx.lineWidth = isHovered ? 2 : 1
      ctx.stroke()

      // Arrow
      const angle = Math.atan2(ty - fy, tx - fx)
      const headLen = 8
      const mx = tx - 20 * Math.cos(angle)
      const my = ty - 20 * Math.sin(angle)
      ctx.beginPath()
      ctx.moveTo(mx, my)
      ctx.lineTo(mx - headLen * Math.cos(angle - Math.PI / 6), my - headLen * Math.sin(angle - Math.PI / 6))
      ctx.lineTo(mx - headLen * Math.cos(angle + Math.PI / 6), my - headLen * Math.sin(angle + Math.PI / 6))
      ctx.closePath()
      ctx.fillStyle = isHovered ? 'rgba(99,102,241,0.6)' : 'rgba(51,65,85,0.4)'
      ctx.fill()
    }

    // Draw nodes
    for (const node of nodes) {
      const nx = (node.x / 1000) * w
      const ny = (node.y / 600) * h
      const isHovered = hoveredNode === node.id
      const color = CATEGORY_COLORS[node.category] || '#94a3b8'
      const radius = isHovered ? 22 : 18

      // Glow
      if (isHovered) {
        ctx.beginPath()
        ctx.arc(nx, ny, radius + 8, 0, Math.PI * 2)
        const glow = ctx.createRadialGradient(nx, ny, radius, nx, ny, radius + 8)
        glow.addColorStop(0, color + '40')
        glow.addColorStop(1, 'transparent')
        ctx.fillStyle = glow
        ctx.fill()
      }

      // Node circle
      ctx.beginPath()
      ctx.arc(nx, ny, radius, 0, Math.PI * 2)
      ctx.fillStyle = isHovered ? color + 'dd' : color + '80'
      ctx.fill()
      ctx.strokeStyle = color
      ctx.lineWidth = isHovered ? 2 : 1
      ctx.stroke()

      // Label
      ctx.font = `${isHovered ? 'bold ' : ''}${isHovered ? 11 : 10}px Inter, sans-serif`
      ctx.fillStyle = isHovered ? '#f1f5f9' : '#94a3b8'
      ctx.textAlign = 'center'
      ctx.fillText(node.label, nx, ny + radius + 16)
    }

    animRef.current = requestAnimationFrame(drawGraph)
  }, [nodes, hoveredNode])

  useEffect(() => {
    animRef.current = requestAnimationFrame(drawGraph)
    return () => cancelAnimationFrame(animRef.current)
  }, [drawGraph])

  const getNodeAt = (x, y) => {
    const canvas = canvasRef.current
    if (!canvas) return null
    const w = canvas.offsetWidth
    const h = canvas.offsetHeight
    for (const node of nodes) {
      const nx = (node.x / 1000) * w
      const ny = (node.y / 600) * h
      const dx = x - nx
      const dy = y - ny
      if (dx * dx + dy * dy < 600) return node.id
    }
    return null
  }

  const handleMouseMove = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    if (dragNode) {
      const w = canvasRef.current.offsetWidth
      const h = canvasRef.current.offsetHeight
      setNodes(prev => prev.map(n =>
        n.id === dragNode
          ? { ...n, x: (x / w) * 1000, y: (y / h) * 600 }
          : n
      ))
    } else {
      const nodeId = getNodeAt(x, y)
      setHoveredNode(nodeId)
      canvasRef.current.style.cursor = nodeId ? 'pointer' : 'default'
    }
  }

  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const nodeId = getNodeAt(e.clientX - rect.left, e.clientY - rect.top)
    if (nodeId) setDragNode(nodeId)
  }

  const handleMouseUp = () => setDragNode(null)

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-bold text-slate-100 mb-1">Policy Knowledge Graph</h3>
        <p className="text-slate-400 text-sm">Interactive network of policy relationships. Drag nodes to reposition.</p>
      </div>

      <div className="glass-card p-2 overflow-hidden">
        <canvas
          ref={canvasRef}
          className="w-full rounded-xl"
          style={{ height: 400 }}
          onMouseMove={handleMouseMove}
          onMouseDown={handleMouseDown}
          onMouseUp={handleMouseUp}
          onMouseLeave={() => { setHoveredNode(null); setDragNode(null) }}
        />
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-3">
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <div key={cat} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-xs text-slate-400 capitalize">{cat}</span>
          </div>
        ))}
      </div>

      {hoveredNode && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-3 text-center"
        >
          <p className="text-sm text-slate-200 font-medium">
            {nodes.find(n => n.id === hoveredNode)?.label}
          </p>
          <p className="text-xs text-slate-500 mt-0.5">
            Connected to {EDGES.filter(e => e.from === hoveredNode || e.to === hoveredNode).length} other policies
          </p>
        </motion.div>
      )}
    </div>
  )
}

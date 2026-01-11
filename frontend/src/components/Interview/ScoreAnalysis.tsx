import { Target, TrendingUp, Award, Zap } from 'lucide-react'
import { motion } from 'framer-motion'

interface ScoreAnalysisProps {
  analysis: {
    keyword_score: number
    sentiment_score: number
    relevance_score: number
    confidence_score: number
    overall_score: number
  }
  feedback: string
}

export default function ScoreAnalysis({ analysis, feedback }: ScoreAnalysisProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return '#007785'
    if (score >= 60) return '#E68523'
    return '#DD5143'
  }

  const scores = [
    { label: 'Keywords', value: analysis.keyword_score, icon: Target, color: '#007785' },
    { label: 'Sentiment', value: analysis.sentiment_score, icon: TrendingUp, color: '#00ACDC' },
    { label: 'Relevance', value: analysis.relevance_score, icon: Award, color: '#E68523' },
    { label: 'Confidence', value: analysis.confidence_score, icon: Zap, color: '#8D6CAB' },
  ]

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl p-6 shadow-lg border"
      style={{ backgroundColor: 'rgba(243, 242, 239, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
    >
      {/* Score global */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold" style={{ color: '#313335' }}>Response Analysis</h3>
        <div className="text-right">
          <div className="text-3xl font-bold" style={{ color: getScoreColor(analysis.overall_score) }}>
            {analysis.overall_score.toFixed(1)}
          </div>
          <div className="text-xs font-semibold" style={{ color: '#888888' }}>/ 100</div>
        </div>
      </div>

      {/* Détails */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {scores.map((score, index) => {
          const Icon = score.icon
          return (
            <div key={index} className="bg-white/80 rounded-xl p-3 border" style={{ borderColor: 'rgba(202, 204, 206, 0.3)' }}>
              <div className="flex items-center gap-2 mb-2">
                <Icon className="w-4 h-4" style={{ color: score.color }} strokeWidth={2.5} />
                <span className="text-xs font-semibold" style={{ color: '#313335' }}>{score.label}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 rounded-full" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${score.value}%` }}
                    transition={{ duration: 0.8, delay: index * 0.1 }}
                    className="h-2 rounded-full"
                    style={{ backgroundColor: score.color }}
                  />
                </div>
                <span className="text-sm font-bold" style={{ color: score.color }}>
                  {score.value.toFixed(0)}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Feedback */}
      <div 
        className="rounded-xl p-4 border-l-4"
        style={{ backgroundColor: 'white', borderColor: getScoreColor(analysis.overall_score) }}
      >
        <p style={{ color: '#313335' }}>{feedback}</p>
      </div>
    </motion.div>
  )
}
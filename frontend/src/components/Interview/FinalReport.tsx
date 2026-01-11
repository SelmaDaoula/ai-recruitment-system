import { Trophy, TrendingUp, Award, Download, ArrowLeft } from 'lucide-react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'

interface FinalReportProps {
  finalScore: {
    final_score: number
    technical_score: number
    behavioral_score: number
    feedback: string
  }
  candidateId: number
}

export default function FinalReport({ finalScore, candidateId }: FinalReportProps) {
  const navigate = useNavigate()

  const getRecommendationStyle = () => {
    if (finalScore.final_score >= 85) {
      return {
        gradient: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)',
        icon: '🌟',
        text: 'Strongly Recommended'
      }
    } else if (finalScore.final_score >= 70) {
      return {
        gradient: 'linear-gradient(135deg, #00ACDC 0%, #8D6CAB 100%)',
        icon: '👍',
        text: 'Recommended'
      }
    } else {
      return {
        gradient: 'linear-gradient(135deg, #E68523 0%, #DD5143 100%)',
        icon: '⚠️',
        text: 'Needs Review'
      }
    }
  }

  const recommendation = getRecommendationStyle()

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="backdrop-blur-xl rounded-3xl border shadow-2xl overflow-hidden max-w-4xl mx-auto"
      style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
    >
      {/* Header */}
      <div 
        className="p-10 text-center text-white"
        style={{ background: recommendation.gradient }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring' }}
          className="text-7xl mb-4"
        >
          {recommendation.icon}
        </motion.div>
        <h2 className="text-4xl font-bold mb-3">Interview Complete!</h2>
        <p className="text-xl opacity-90">{recommendation.text}</p>
      </div>

      {/* Scores */}
      <div className="p-10">
        {/* Score Global */}
        <div className="text-center mb-10">
          <div className="text-7xl font-bold mb-3" style={{ color: '#007785' }}>
            {finalScore.final_score.toFixed(1)}
          </div>
          <div className="text-xl font-semibold" style={{ color: '#888888' }}>Overall Score / 100</div>
        </div>

        {/* Détails */}
        <div className="grid grid-cols-2 gap-6 mb-8">
          <div 
            className="rounded-2xl p-8 text-center"
            style={{ background: 'linear-gradient(135deg, rgba(0, 119, 133, 0.1) 0%, rgba(0, 172, 220, 0.1) 100%)' }}
          >
            <TrendingUp className="w-10 h-10 mx-auto mb-3" style={{ color: '#007785' }} strokeWidth={2.5} />
            <div className="text-4xl font-bold mb-2" style={{ color: '#007785' }}>
              {finalScore.technical_score.toFixed(1)}
            </div>
            <div className="text-sm font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>
              Technical Skills
            </div>
          </div>

          <div 
            className="rounded-2xl p-8 text-center"
            style={{ background: 'linear-gradient(135deg, rgba(141, 108, 171, 0.1) 0%, rgba(230, 133, 35, 0.1) 100%)' }}
          >
            <Award className="w-10 h-10 mx-auto mb-3" style={{ color: '#8D6CAB' }} strokeWidth={2.5} />
            <div className="text-4xl font-bold mb-2" style={{ color: '#8D6CAB' }}>
              {finalScore.behavioral_score.toFixed(1)}
            </div>
            <div className="text-sm font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>
              Soft Skills
            </div>
          </div>
        </div>

        {/* Feedback */}
        <div 
          className="rounded-2xl p-6 mb-8"
          style={{ background: 'linear-gradient(135deg, rgba(0, 119, 133, 0.05) 0%, rgba(141, 108, 171, 0.05) 100%)' }}
        >
          <p className="text-lg leading-relaxed" style={{ color: '#313335' }}>{finalScore.feedback}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-4">
          <button 
            onClick={() => navigate(`/candidates/${candidateId}`)}
            className="flex-1 py-4 rounded-xl font-semibold transition-all hover:scale-105 flex items-center justify-center gap-2"
            style={{ backgroundColor: 'rgba(136, 136, 136, 0.1)', color: '#888888' }}
          >
            <ArrowLeft className="w-5 h-5" strokeWidth={2.5} />
            View Candidate Profile
          </button>
          <button 
            className="flex-1 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 flex items-center justify-center gap-2"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            <Download className="w-5 h-5" strokeWidth={2.5} />
            Download Report
          </button>
        </div>
      </div>
    </motion.div>
  )
}
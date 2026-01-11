import { MessageSquare, Brain, Zap } from 'lucide-react'

interface QuestionCardProps {
  question: string
  category: string
  difficulty: string
}

export default function QuestionCard({ question, category, difficulty }: QuestionCardProps) {
  const getCategoryIcon = () => {
    switch (category) {
      case 'welcome': return <MessageSquare className="w-5 h-5" strokeWidth={2.5} />
      case 'technical': return <Brain className="w-5 h-5" strokeWidth={2.5} />
      case 'behavioral': return <Zap className="w-5 h-5" strokeWidth={2.5} />
      default: return <MessageSquare className="w-5 h-5" strokeWidth={2.5} />
    }
  }

  const getCategoryColor = () => {
    switch (category) {
      case 'welcome': return { bg: 'rgba(0, 172, 220, 0.1)', text: '#00ACDC' }
      case 'technical': return { bg: 'rgba(0, 119, 133, 0.1)', text: '#007785' }
      case 'behavioral': return { bg: 'rgba(141, 108, 171, 0.1)', text: '#8D6CAB' }
      default: return { bg: 'rgba(136, 136, 136, 0.1)', text: '#888888' }
    }
  }

  const colors = getCategoryColor()

  return (
    <div className="flex justify-start">
      <div 
        className="max-w-2xl rounded-2xl rounded-tl-sm p-6 shadow-lg border"
        style={{ backgroundColor: 'rgba(243, 242, 239, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <div className="flex items-center gap-3 mb-3">
          <div 
            className="p-2 rounded-xl"
            style={{ backgroundColor: colors.bg, color: colors.text }}
          >
            {getCategoryIcon()}
          </div>
          <div>
            <span className="text-sm font-semibold capitalize" style={{ color: colors.text }}>
              {category}
            </span>
            <span 
              className="ml-2 text-xs px-2 py-0.5 rounded-full font-bold capitalize"
              style={{ 
                backgroundColor: difficulty === 'easy' ? 'rgba(0, 172, 220, 0.2)' : 
                                difficulty === 'medium' ? 'rgba(230, 133, 35, 0.2)' : 
                                'rgba(221, 81, 67, 0.2)',
                color: difficulty === 'easy' ? '#00ACDC' : 
                      difficulty === 'medium' ? '#E68523' : '#DD5143'
              }}
            >
              {difficulty}
            </span>
          </div>
        </div>
        <p className="text-lg leading-relaxed" style={{ color: '#313335' }}>
          {question}
        </p>
      </div>
    </div>
  )
}
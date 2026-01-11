import { useState, useEffect, useRef } from 'react'
import { Send, Loader2, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { interviewApi } from '../../services/api'
import QuestionCard from './QuestionCard'
import ResponseInput from './ResponseInput'
import ScoreAnalysis from './ScoreAnalysis'
import ProgressBar from './ProgressBar'
import FinalReport from './FinalReport'
import { useQuery } from '@tanstack/react-query'


interface Message {
  type: 'bot' | 'user' | 'feedback' | 'error'
  text?: string
  category?: string
  difficulty?: string
  score?: any
  feedback?: string
  timestamp: Date
}

interface InterviewChatProps {
  candidateId: number
  jobOfferId: number
}

export default function InterviewChat({ candidateId, jobOfferId }: InterviewChatProps) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [currentQuestion, setCurrentQuestion] = useState<any>(null)
  const [userInput, setUserInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState({ current: 0, total: 12 })
  const [isCompleted, setIsCompleted] = useState(false)
  const [finalScore, setFinalScore] = useState<any>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Démarrer l'entretien
  useEffect(() => {
    const initInterview = async () => {
      try {
        setLoading(true)
        const data = await interviewApi.start(candidateId, jobOfferId)
        
        setSessionId(data.session_id)
        setCurrentQuestion(data)
        setProgress({ current: data.current_question, total: data.total_questions })
        
        setMessages([{
          type: 'bot',
          text: data.question_text,
          category: data.category,
          difficulty: data.difficulty,
          timestamp: new Date()
        }])
      } catch (error) {
        console.error('Error starting interview:', error)
        setMessages([{
          type: 'error',
          text: 'Failed to start interview. Please try again.',
          timestamp: new Date()
        }])
      } finally {
        setLoading(false)
      }
    }

    initInterview()
  }, [candidateId, jobOfferId])

  // Envoyer réponse
const handleSendResponse = async () => {
  if (!userInput.trim() || loading || !sessionId || !currentQuestion) return

  const userMessage = userInput
  setUserInput('')
  setLoading(true)

  // Ajouter message utilisateur
  setMessages(prev => [...prev, {
    type: 'user',
    text: userMessage,
    timestamp: new Date()
  }])

  try {
    const data = await interviewApi.respond(sessionId, currentQuestion.question_id, userMessage)

    // Ajouter feedback
    setMessages(prev => [...prev, {
      type: 'feedback',
      score: data.analysis,
      feedback: data.feedback,
      timestamp: new Date()
    }])

    // ✅ CORRECTION : Vérifier si terminé
    if (data.next_question?.status === 'completed') {
      // ✅ Récupérer le score final via l'API
      try {
        const scoreData = await interviewApi.getScore(sessionId)
        console.log('✅ Score final récupéré:', scoreData)
        setIsCompleted(true)
        setFinalScore(scoreData)
      } catch (scoreError) {
        console.error('❌ Erreur récupération score:', scoreError)
        // Fallback : utiliser les données disponibles
        setIsCompleted(true)
        setFinalScore({
          final_score: data.next_question.final_score || 0,
          technical_score: data.next_question.technical_score || 0,
          behavioral_score: data.next_question.behavioral_score || 0,
          feedback: data.next_question.feedback || 'Interview terminé'
        })
      }
    } else {
      // Prochaine question
      setCurrentQuestion(data.next_question)
      setProgress({ 
        current: data.next_question.current_question, 
        total: data.next_question.total_questions 
      })

      setMessages(prev => [...prev, {
        type: 'bot',
        text: data.next_question.question_text,
        category: data.next_question.category,
        difficulty: data.next_question.difficulty,
        timestamp: new Date()
      }])
    }
  } catch (error) {
    console.error('Error sending response:', error)
    setMessages(prev => [...prev, {
      type: 'error',
      text: 'Failed to send response. Please try again.',
      timestamp: new Date()
    }])
  } finally {
    setLoading(false)
  }
}
  if (isCompleted && finalScore) {
    return <FinalReport finalScore={finalScore} candidateId={candidateId} />
  }

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Chat Area */}
      <div className="col-span-8 space-y-6">
        {/* Progress */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <ProgressBar current={progress.current} total={progress.total} />
        </div>

        {/* Messages */}
        <div 
          className="backdrop-blur-xl rounded-2xl border shadow-xl overflow-hidden"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <div className="h-[600px] overflow-y-auto p-6 space-y-4">
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  {message.type === 'bot' && (
                    <QuestionCard 
                      question={message.text!}
                      category={message.category!}
                      difficulty={message.difficulty!}
                    />
                  )}

                  {message.type === 'user' && (
                    <div className="flex justify-end">
                      <div 
                        className="max-w-2xl px-6 py-4 rounded-2xl rounded-tr-sm shadow-lg"
                        style={{ backgroundColor: '#007785' }}
                      >
                        <p className="text-white whitespace-pre-wrap">{message.text}</p>
                        <span className="text-xs text-white/70 mt-2 block">
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  )}

                  {message.type === 'feedback' && (
                    <ScoreAnalysis 
                      analysis={message.score}
                      feedback={message.feedback!}
                    />
                  )}

                  {message.type === 'error' && (
                    <div 
                      className="p-4 rounded-xl border-l-4"
                      style={{ backgroundColor: 'rgba(221, 81, 67, 0.1)', borderColor: '#DD5143' }}
                    >
                      <p style={{ color: '#DD5143' }}>{message.text}</p>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {loading && (
              <div className="flex items-center justify-center space-x-2 p-4" style={{ color: '#888888' }}>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Analyzing your response...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input */}
        <ResponseInput
          value={userInput}
          onChange={setUserInput}
          onSend={handleSendResponse}
          loading={loading}
        />
      </div>

      {/* Sidebar Info */}
      <div className="col-span-4 space-y-6">
        {/* Tips Card */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <div className="flex items-center gap-3 mb-4">
            <div 
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
            >
              <Sparkles className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
            <h3 className="text-lg font-bold" style={{ color: '#313335' }}>Tips for Success</h3>
          </div>
          <ul className="space-y-3 text-sm" style={{ color: '#888888' }}>
            <li className="flex items-start gap-2">
              <span style={{ color: '#007785' }}>•</span>
              <span>Be specific and mention concrete examples</span>
            </li>
            <li className="flex items-start gap-2">
              <span style={{ color: '#00ACDC' }}>•</span>
              <span>Include technical terms and technologies</span>
            </li>
            <li className="flex items-start gap-2">
              <span style={{ color: '#E68523' }}>•</span>
              <span>Quantify your achievements with numbers</span>
            </li>
            <li className="flex items-start gap-2">
              <span style={{ color: '#8D6CAB' }}>•</span>
              <span>Show confidence in your answers</span>
            </li>
          </ul>
        </div>

        {/* Current Question Info */}
        {currentQuestion && (
          <div 
            className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
            style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
          >
            <h3 className="text-lg font-bold mb-4" style={{ color: '#313335' }}>Question Details</h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: '#888888' }}>Category</p>
                <span 
                  className="px-3 py-1 rounded-lg text-sm font-bold capitalize"
                  style={{ 
                    backgroundColor: currentQuestion.category === 'technical' ? 'rgba(0, 119, 133, 0.1)' : 
                                    currentQuestion.category === 'behavioral' ? 'rgba(141, 108, 171, 0.1)' : 
                                    'rgba(0, 172, 220, 0.1)',
                    color: currentQuestion.category === 'technical' ? '#007785' : 
                          currentQuestion.category === 'behavioral' ? '#8D6CAB' : '#00ACDC'
                  }}
                >
                  {currentQuestion.category}
                </span>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: '#888888' }}>Difficulty</p>
                <span 
                  className="px-3 py-1 rounded-lg text-sm font-bold capitalize"
                  style={{ 
                    backgroundColor: currentQuestion.difficulty === 'easy' ? 'rgba(0, 172, 220, 0.1)' : 
                                    currentQuestion.difficulty === 'medium' ? 'rgba(230, 133, 35, 0.1)' : 
                                    'rgba(221, 81, 67, 0.1)',
                    color: currentQuestion.difficulty === 'easy' ? '#00ACDC' : 
                          currentQuestion.difficulty === 'medium' ? '#E68523' : '#DD5143'
                  }}
                >
                  {currentQuestion.difficulty}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  MessageSquare, ArrowLeft, Briefcase, User, Sparkles, 
  Brain, TrendingUp, Clock, CheckCircle, Target
} from 'lucide-react'
import InterviewChat from '../components/Interview/InterviewChat'
import { candidatesApi, jobsApi } from '../services/api'

export default function InterviewPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const candidateId = searchParams.get('candidate')
  const jobId = searchParams.get('job')
  const [isStarting, setIsStarting] = useState(true)

  // Charger les données du candidat et du job
  const { data: candidate } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => candidatesApi.getById(Number(candidateId)),
    enabled: !!candidateId
  })

  const { data: job } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.getById(Number(jobId)),
    enabled: !!jobId
  })

  useEffect(() => {
    // Animation de démarrage
    const timer = setTimeout(() => setIsStarting(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  if (!candidateId || !jobId) {
    return (
      <div className="flex items-center justify-center h-[80vh]">
        <div 
          className="backdrop-blur-xl rounded-3xl p-12 border shadow-2xl text-center max-w-lg"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <div 
            className="w-24 h-24 mx-auto mb-6 rounded-2xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #8D6CAB 0%, #007785 100%)' }}
          >
            <MessageSquare className="w-12 h-12 text-white" strokeWidth={2.5} />
          </div>
          <h2 className="text-2xl font-bold mb-3" style={{ color: '#313335' }}>
            No Interview Selected
          </h2>
          <p className="mb-6" style={{ color: '#888888' }}>
            Please select a candidate from the candidates page to start an interview
          </p>
          <button
            onClick={() => navigate('/candidates')}
            className="px-8 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 hover:shadow-2xl"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            Browse Candidates
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Header Premium avec informations détaillées */}
      <div 
        className="relative overflow-hidden rounded-3xl shadow-2xl"
        style={{ background: 'linear-gradient(135deg, #8D6CAB 0%, #007785 100%)' }}
      >
        {/* Pattern de fond animé */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}></div>
        </div>

        {/* Gradient overlay subtil */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent"></div>
        
        <div className="relative p-8">
          {/* Ligne du haut : Navigation + Statut */}
          <div className="flex items-center justify-between mb-8">
            <button
              onClick={() => navigate('/candidates')}
              className="group flex items-center gap-3 px-4 py-2 rounded-xl backdrop-blur-xl border transition-all hover:scale-105"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <ArrowLeft className="w-5 h-5 text-white group-hover:-translate-x-1 transition-transform" strokeWidth={2.5} />
              <span className="text-white font-semibold text-sm">Back to Candidates</span>
            </button>

            <div className="flex items-center gap-3">
              {/* Badge Live */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl backdrop-blur-xl border animate-pulse"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.2)',
                  borderColor: 'rgba(255, 255, 255, 0.3)'
                }}
              >
                <div className="w-2 h-2 rounded-full bg-green-400 animate-ping absolute"></div>
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                <span className="text-white font-semibold text-sm">Live Interview</span>
              </div>

              {/* Badge AI Powered */}
              <div className="flex items-center gap-2 px-4 py-2 rounded-xl backdrop-blur-xl border"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  borderColor: 'rgba(255, 255, 255, 0.2)'
                }}
              >
                <Sparkles className="w-4 h-4 text-yellow-300" strokeWidth={2.5} />
                <span className="text-white font-semibold text-sm">AI Powered</span>
              </div>
            </div>
          </div>

          {/* Contenu principal */}
          <div className="flex items-start gap-8">
            {/* Icône principale */}
            <div 
              className="w-20 h-20 rounded-2xl backdrop-blur-xl flex items-center justify-center border shadow-2xl"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                borderColor: 'rgba(255, 255, 255, 0.3)'
              }}
            >
              <MessageSquare className="w-10 h-10 text-white" strokeWidth={2.5} />
            </div>

            {/* Texte */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <h1 className="text-4xl font-bold text-white">
                  AI Interview Assistant
                </h1>
                <div className="px-3 py-1 rounded-lg text-xs font-bold text-white"
                  style={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }}
                >
                  BETA
                </div>
              </div>
              <p className="text-white/90 text-lg mb-4">
                Intelligent conversation analysis powered by advanced NLP and ML algorithms
              </p>

              {/* Badges de fonctionnalités */}
              <div className="flex items-center gap-3 flex-wrap">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg backdrop-blur-sm"
                  style={{ backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
                >
                  <Brain className="w-4 h-4 text-white" strokeWidth={2.5} />
                  <span className="text-white text-sm font-medium">NLP Analysis</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg backdrop-blur-sm"
                  style={{ backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
                >
                  <TrendingUp className="w-4 h-4 text-white" strokeWidth={2.5} />
                  <span className="text-white text-sm font-medium">Real-time Scoring</span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg backdrop-blur-sm"
                  style={{ backgroundColor: 'rgba(255, 255, 255, 0.15)' }}
                >
                  <Target className="w-4 h-4 text-white" strokeWidth={2.5} />
                  <span className="text-white text-sm font-medium">Adaptive Questions</span>
                </div>
              </div>
            </div>
          </div>

          {/* Informations Candidat & Job en bas */}
          {(candidate || job) && (
            <div className="mt-8 pt-6 border-t grid grid-cols-2 gap-6"
              style={{ borderColor: 'rgba(255, 255, 255, 0.2)' }}
            >
              {/* Candidat */}
              {candidate && (
                <div className="flex items-center gap-4">
                  <div 
                    className="w-14 h-14 rounded-xl flex items-center justify-center border shadow-lg"
                    style={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.2)',
                      borderColor: 'rgba(255, 255, 255, 0.3)'
                    }}
                  >
                    <User className="w-7 h-7 text-white" strokeWidth={2.5} />
                  </div>
                  <div>
                    <p className="text-white/70 text-sm font-semibold mb-1">CANDIDATE</p>
                    <p className="text-white text-lg font-bold">
                      {candidate.first_name} {candidate.last_name}
                    </p>
                    <p className="text-white/80 text-sm">{candidate.email}</p>
                  </div>
                </div>
              )}

              {/* Job */}
              {job && (
                <div className="flex items-center gap-4">
                  <div 
                    className="w-14 h-14 rounded-xl flex items-center justify-center border shadow-lg"
                    style={{ 
                      backgroundColor: 'rgba(255, 255, 255, 0.2)',
                      borderColor: 'rgba(255, 255, 255, 0.3)'
                    }}
                  >
                    <Briefcase className="w-7 h-7 text-white" strokeWidth={2.5} />
                  </div>
                  <div>
                    <p className="text-white/70 text-sm font-semibold mb-1">POSITION</p>
                    <p className="text-white text-lg font-bold">{job.title}</p>
                    <p className="text-white/80 text-sm">{job.location}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Barre d'informations */}
      <div className="grid grid-cols-3 gap-4">
        {/* Info 1 */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-5 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: 'rgba(0, 119, 133, 0.15)' }}
            >
              <Clock className="w-5 h-5" style={{ color: '#007785' }} strokeWidth={2.5} />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: '#888888' }}>
              Duration
            </span>
          </div>
          <p className="text-2xl font-bold" style={{ color: '#313335' }}>
            ~15 min
          </p>
          <p className="text-sm mt-1" style={{ color: '#888888' }}>
            Average completion time
          </p>
        </div>

        {/* Info 2 */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-5 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: 'rgba(0, 172, 220, 0.15)' }}
            >
              <MessageSquare className="w-5 h-5" style={{ color: '#00ACDC' }} strokeWidth={2.5} />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: '#888888' }}>
              Questions
            </span>
          </div>
          <p className="text-2xl font-bold" style={{ color: '#313335' }}>
            10-12
          </p>
          <p className="text-sm mt-1" style={{ color: '#888888' }}>
            Personalized for this role
          </p>
        </div>

        {/* Info 3 */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-5 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ backgroundColor: 'rgba(141, 108, 171, 0.15)' }}
            >
              <CheckCircle className="w-5 h-5" style={{ color: '#8D6CAB' }} strokeWidth={2.5} />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider" style={{ color: '#888888' }}>
              Analysis
            </span>
          </div>
          <p className="text-2xl font-bold" style={{ color: '#313335' }}>
            Real-time
          </p>
          <p className="text-sm mt-1" style={{ color: '#888888' }}>
            Instant AI feedback
          </p>
        </div>
      </div>

      {/* Message d'introduction (apparait au début) */}
      {isStarting && (
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border animate-fade-in"
          style={{ 
            backgroundColor: 'rgba(0, 172, 220, 0.1)',
            borderColor: 'rgba(0, 172, 220, 0.3)'
          }}
        >
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #00ACDC 0%, #007785 100%)' }}
            >
              <Sparkles className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h3 className="text-lg font-bold mb-2" style={{ color: '#007785' }}>
                🎯 Ready to Start?
              </h3>
              <p style={{ color: '#313335' }}>
                This AI-powered interview will evaluate technical skills, problem-solving abilities, 
                and behavioral competencies. Answer naturally and take your time. The system will 
                analyze your responses in real-time and provide instant feedback.
              </p>
              <div className="flex items-center gap-2 mt-4">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
                  style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)' }}
                >
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#007785' }}></div>
                  <span className="text-sm font-semibold" style={{ color: '#007785' }}>
                    Be specific and detailed
                  </span>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
                  style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)' }}
                >
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: '#007785' }}></div>
                  <span className="text-sm font-semibold" style={{ color: '#007785' }}>
                    Use concrete examples
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interface de Chat */}
      <InterviewChat 
        candidateId={Number(candidateId)} 
        jobOfferId={Number(jobId)} 
      />
    </div>
  )
}
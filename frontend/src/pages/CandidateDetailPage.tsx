import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { candidatesApi } from '../services/api'
import { 
  ArrowLeft, Mail, Phone, Award, TrendingUp, Calendar, 
  Download, FileText, AlertCircle, Briefcase, GraduationCap,
  Globe, Target, CheckCircle2, BarChart3, Star, MessageSquare
} from 'lucide-react'

export default function CandidateDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()

  const { data: candidate, isLoading, isError } = useQuery({
    queryKey: ['candidate', id],
    queryFn: () => candidatesApi.getById(Number(id)),
    retry: false,
  })

  const { data: analysis } = useQuery({
    queryKey: ['candidate-analysis', id],
    queryFn: () => candidatesApi.getImprovedAnalysis(Number(id)),
    enabled: !!candidate,
    retry: false,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full" style={{ border: '4px solid #CACCCE' }}></div>
          <div className="absolute inset-0 rounded-full animate-spin" style={{ border: '4px solid #007785', borderTopColor: 'transparent' }}></div>
        </div>
      </div>
    )
  }

  if (isError || !candidate) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div 
          className="backdrop-blur-xl rounded-3xl p-12 border shadow-2xl max-w-md w-full text-center"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <div className="w-20 h-20 rounded-full mx-auto mb-6 flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #DD5143 0%, #E68523 100%)' }}
          >
            <AlertCircle className="w-10 h-10 text-white" strokeWidth={2.5} />
          </div>
          
          <h2 className="text-3xl font-bold mb-4" style={{ color: '#313335' }}>
            Candidat introuvable
          </h2>
          
          <p className="mb-8 text-lg" style={{ color: '#888888' }}>
            Le candidat #{id} n'existe pas ou a été supprimé.
          </p>
          
          <button
            onClick={() => navigate(-1)}
            className="w-full px-6 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 flex items-center justify-center gap-2"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            <ArrowLeft className="w-5 h-5" strokeWidth={2.5} />
            Retour
          </button>
        </div>
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#007785'
    if (score >= 65) return '#00ACDC'
    if (score >= 50) return '#E68523'
    return '#DD5143'
  }

  const getCategoryInfo = (category: string) => {
    const info = {
      'A': { 
        label: 'Excellent',
        bg: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)',
        icon: Star
      },
      'B': { 
        label: 'Bon',
        bg: 'linear-gradient(135deg, #00ACDC 0%, #8D6CAB 100%)',
        icon: TrendingUp
      },
      'C': { 
        label: 'Moyen',
        bg: 'linear-gradient(135deg, #E68523 0%, #F5A623 100%)',
        icon: Award
      },
      'D': { 
        label: 'Faible',
        bg: 'linear-gradient(135deg, #DD5143 0%, #E68523 100%)',
        icon: AlertCircle
      }
    }
    return info[category as keyof typeof info] || info['D']
  }

  const handleDownloadCV = () => {
    window.open(`http://localhost:8000/api/candidates/${candidate.id}/download-cv`, '_blank')
  }

  const scoreBreakdown = analysis?.score_breakdown || candidate.score_breakdown || {}
  const recommendation = analysis?.recommendation || 'N/A'
  const category = analysis?.category || (candidate.cv_score >= 80 ? 'A' : candidate.cv_score >= 65 ? 'B' : candidate.cv_score >= 50 ? 'C' : 'D')
  const categoryInfo = getCategoryInfo(category)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div 
        className="relative overflow-hidden rounded-3xl p-8 shadow-2xl"
        style={{ background: 'linear-gradient(135deg, #007785 0%, #8D6CAB 100%)' }}
      >
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}></div>
        </div>
        
        <div className="relative">
          <div className="flex items-start justify-between mb-6">
            <button
              onClick={() => navigate(-1)}
              className="w-12 h-12 rounded-xl backdrop-blur-xl flex items-center justify-center border transition-all hover:scale-110"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <ArrowLeft className="w-6 h-6 text-white" strokeWidth={2.5} />
            </button>

            {/* ✅ BOUTONS D'ACTION */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleDownloadCV}
                className="px-5 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
                style={{ backgroundColor: 'white', color: '#007785' }}
              >
                <Download className="w-5 h-5" strokeWidth={2.5} />
                Download CV
              </button>
              
              {/* ✅ BOUTON START INTERVIEW */}
              <button
  onClick={() => {
    if (!candidate.job_offer_id) {
      alert('❌ Erreur : Ce candidat n\'est pas associé à une offre d\'emploi')
      return
    }
    navigate(`/interviews?candidate=${candidate.id}&job=${candidate.job_offer_id}`)
  }}
  className="px-6 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
  style={{ 
    background: 'linear-gradient(135deg, #8D6CAB 0%, #007785 100%)',
    color: 'white'
  }}
>
  <MessageSquare className="w-5 h-5" strokeWidth={2.5} />
  Start Interview
</button>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div 
              className="w-24 h-24 rounded-2xl flex items-center justify-center text-white text-4xl font-bold shadow-2xl flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%)' }}
            >
              {candidate.first_name?.[0]}{candidate.last_name?.[0]}
            </div>
            
            <div className="flex-1">
              <h1 className="text-4xl font-bold text-white mb-3">
                {candidate.first_name} {candidate.last_name}
              </h1>
              
              <div className="flex flex-wrap items-center gap-4 text-white/90">
                {candidate.email && (
                  <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg">
                    <Mail className="w-4 h-4" strokeWidth={2} />
                    <span className="text-sm">{candidate.email}</span>
                  </div>
                )}
                {candidate.phone && (
                  <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg">
                    <Phone className="w-4 h-4" strokeWidth={2} />
                    <span className="text-sm">{candidate.phone}</span>
                  </div>
                )}
                {analysis?.job_title && (
                  <div className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-3 py-1.5 rounded-lg">
                    <Target className="w-4 h-4" strokeWidth={2} />
                    <span className="text-sm font-semibold">{analysis.job_title}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Score Overview - 2 colonnes */}
      <div className="grid grid-cols-2 gap-6">
        {/* Score Principal */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-8 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)'
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-wider mb-2" style={{ color: '#888888' }}>
                Score Global
              </p>
              <div className="flex items-baseline gap-2">
                <span className="text-6xl font-bold" style={{ color: getScoreColor(candidate.cv_score) }}>
                  {candidate.cv_score?.toFixed(0)}
                </span>
                <span className="text-3xl font-semibold" style={{ color: '#888888' }}>/100</span>
              </div>
            </div>
            <div className="w-20 h-20 rounded-2xl flex items-center justify-center" 
              style={{ background: categoryInfo.bg }}>
              <Award className="w-10 h-10 text-white" strokeWidth={2.5} />
            </div>
          </div>
          
          {/* Progress bar */}
          <div className="h-4 rounded-full mt-6" style={{ backgroundColor: 'rgba(202, 204, 206, 0.2)' }}>
            <div 
              className="h-full rounded-full transition-all duration-1000"
              style={{ 
                width: `${candidate.cv_score}%`,
                background: `linear-gradient(90deg, ${getScoreColor(candidate.cv_score)} 0%, ${getScoreColor(candidate.cv_score)}dd 100%)`
              }}
            ></div>
          </div>
        </div>

        {/* Catégorie et Recommandation */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-8 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)'
          }}
        >
          <div className="flex items-start gap-4">
            <div 
              className="w-16 h-16 rounded-xl flex items-center justify-center text-white flex-shrink-0"
              style={{ background: categoryInfo.bg }}
            >
              <categoryInfo.icon className="w-8 h-8" strokeWidth={2.5} />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#888888' }}>
                  Catégorie
                </span>
                <span 
                  className="px-4 py-1.5 rounded-xl text-xl font-bold text-white"
                  style={{ background: categoryInfo.bg }}
                >
                  {category}
                </span>
              </div>
              
              <p className="text-sm font-semibold mb-2" style={{ color: '#888888' }}>
                Recommandation
              </p>
              <p className="text-base font-semibold leading-relaxed" style={{ color: '#313335' }}>
                {recommendation}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Détail des scores */}
      {Object.keys(scoreBreakdown).length > 0 && (
        <div 
          className="backdrop-blur-xl rounded-2xl p-8 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
            >
              <BarChart3 className="w-6 h-6 text-white" strokeWidth={2.5} />
            </div>
            <h2 className="text-2xl font-bold" style={{ color: '#313335' }}>
              Détail de l'évaluation
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {Object.entries(scoreBreakdown).map(([key, value]) => {
              const score = value as number
              const labels: Record<string, { name: string, icon: any }> = {
                skills: { name: 'Compétences techniques', icon: Briefcase },
                experience: { name: 'Années d\'expérience', icon: Award },
                education: { name: 'Formation académique', icon: GraduationCap },
                languages: { name: 'Compétences linguistiques', icon: Globe }
              }
              
              const info = labels[key] || { name: key, icon: Award }
              const Icon = info.icon
              
              return (
                <div 
                  key={key}
                  className="p-5 rounded-xl border transition-all hover:shadow-lg"
                  style={{ 
                    backgroundColor: 'rgba(243, 242, 239, 0.5)',
                    borderColor: 'rgba(202, 204, 206, 0.3)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-3">
                    <div 
                      className="w-10 h-10 rounded-lg flex items-center justify-center"
                      style={{ backgroundColor: `${getScoreColor(score)}15` }}
                    >
                      <Icon className="w-5 h-5" style={{ color: getScoreColor(score) }} strokeWidth={2} />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-semibold" style={{ color: '#888888' }}>
                        {info.name}
                      </p>
                    </div>
                    <span className="text-2xl font-bold" style={{ color: getScoreColor(score) }}>
                      {score}
                    </span>
                  </div>
                  
                  <div className="h-2.5 rounded-full" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}>
                    <div 
                      className="h-full rounded-full transition-all duration-500"
                      style={{ 
                        width: `${score}%`,
                        backgroundColor: getScoreColor(score)
                      }}
                    ></div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Informations extraites - Grid 2 colonnes */}
      {(analysis?.extracted_data || candidate.extracted_data) && (
        <div className="grid grid-cols-2 gap-6">
          {/* Colonne gauche : Compétences + Expérience */}
          <div className="space-y-6">
            {/* Compétences */}
            {(analysis?.extracted_data?.skills || candidate.extracted_data?.skills)?.length > 0 && (
              <div 
                className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
                style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)' }}
                  >
                    <Briefcase className="w-5 h-5" style={{ color: '#007785' }} strokeWidth={2} />
                  </div>
                  <h3 className="text-lg font-bold" style={{ color: '#313335' }}>
                    Compétences ({(analysis?.extracted_data?.skills || candidate.extracted_data.skills).length})
                  </h3>
                </div>
                
                <div className="flex flex-wrap gap-2">
                  {(analysis?.extracted_data?.skills || candidate.extracted_data.skills).map((skill: string, idx: number) => (
                    <span 
                      key={idx} 
                      className="px-3 py-2 rounded-lg text-sm font-semibold transition-all hover:scale-105" 
                      style={{ 
                        backgroundColor: 'rgba(0, 119, 133, 0.1)', 
                        color: '#007785',
                        border: '1px solid rgba(0, 119, 133, 0.2)'
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Expérience */}
            {(analysis?.extracted_data?.experience_years || candidate.extracted_data?.experience_years) !== undefined && (
              <div 
                className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
                style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(0, 172, 220, 0.1)' }}
                  >
                    <Award className="w-5 h-5" style={{ color: '#00ACDC' }} strokeWidth={2} />
                  </div>
                  <h3 className="text-lg font-bold" style={{ color: '#313335' }}>
                    Expérience professionnelle
                  </h3>
                </div>
                
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold" style={{ color: '#00ACDC' }}>
                    {analysis?.extracted_data?.experience_years || candidate.extracted_data.experience_years}
                  </span>
                  <span className="text-xl font-semibold" style={{ color: '#888888' }}>
                    années
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Colonne droite : Formation + Langues */}
          <div className="space-y-6">
            {/* Formation */}
            {(analysis?.extracted_data?.education || candidate.extracted_data?.education)?.length > 0 && (
              <div 
                className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
                style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(141, 108, 171, 0.1)' }}
                  >
                    <GraduationCap className="w-5 h-5" style={{ color: '#8D6CAB' }} strokeWidth={2} />
                  </div>
                  <h3 className="text-lg font-bold" style={{ color: '#313335' }}>
                    Formation
                  </h3>
                </div>
                
                <div className="space-y-3">
                  {(analysis?.extracted_data?.education || candidate.extracted_data.education).map((edu: any, idx: number) => (
                    <div 
                      key={idx} 
                      className="p-3 rounded-lg transition-all hover:shadow-md"
                      style={{ backgroundColor: 'rgba(141, 108, 171, 0.05)' }}
                    >
                      <p className="font-semibold" style={{ color: '#313335' }}>
                        {typeof edu === 'string' ? edu : `${edu.degree || 'Diplôme'}`}
                      </p>
                      {typeof edu !== 'string' && edu.field && (
                        <p className="text-sm mt-1" style={{ color: '#888888' }}>
                          {edu.field}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Langues */}
            {(analysis?.extracted_data?.languages || candidate.extracted_data?.languages)?.length > 0 && (
              <div 
                className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
                style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: 'rgba(230, 133, 35, 0.1)' }}
                  >
                    <Globe className="w-5 h-5" style={{ color: '#E68523' }} strokeWidth={2} />
                  </div>
                  <h3 className="text-lg font-bold" style={{ color: '#313335' }}>
                    Langues
                  </h3>
                </div>
                
                <div className="space-y-2">
                  {(analysis?.extracted_data?.languages || candidate.extracted_data.languages).map((lang: any, idx: number) => (
                    <div 
                      key={idx} 
                      className="flex items-center justify-between p-3 rounded-lg transition-all hover:shadow-md"
                      style={{ backgroundColor: 'rgba(230, 133, 35, 0.05)' }}
                    >
                      <span className="font-semibold" style={{ color: '#313335' }}>
                        {lang.language || lang.name}
                      </span>
                      <span 
                        className="px-3 py-1 rounded-lg text-sm font-semibold"
                        style={{ backgroundColor: 'rgba(230, 133, 35, 0.15)', color: '#E68523' }}
                      >
                        {lang.level}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Date de candidature */}
            <div 
              className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.9)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)' }}
                >
                  <Calendar className="w-5 h-5" style={{ color: '#007785' }} strokeWidth={2} />
                </div>
                <h3 className="text-lg font-bold" style={{ color: '#313335' }}>
                  Candidature
                </h3>
              </div>
              
              <p className="text-xl font-bold" style={{ color: '#313335' }}>
                {new Date(candidate.applied_at).toLocaleDateString('fr-FR', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
              <p className="text-sm mt-1" style={{ color: '#888888' }}>
                Il y a {Math.floor((Date.now() - new Date(candidate.applied_at).getTime()) / (1000 * 60 * 60 * 24))} jours
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ✅ SECTION CALL-TO-ACTION - START INTERVIEW */}
      <div 
        className="backdrop-blur-xl rounded-2xl p-8 border shadow-xl text-center"
        style={{ 
          background: 'linear-gradient(135deg, rgba(141, 108, 171, 0.1) 0%, rgba(0, 119, 133, 0.1) 100%)',
          borderColor: 'rgba(141, 108, 171, 0.3)',
          borderWidth: '2px'
        }}
      >
        <div className="flex items-center justify-center mb-4">
          <div 
            className="w-16 h-16 rounded-2xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #8D6CAB 0%, #007785 100%)' }}
          >
            <MessageSquare className="w-8 h-8 text-white" strokeWidth={2.5} />
          </div>
        </div>
        
        <h3 className="text-2xl font-bold mb-3" style={{ color: '#313335' }}>
          Prêt à évaluer ce candidat ?
        </h3>
        <p className="text-lg mb-6" style={{ color: '#888888' }}>
          Lancez un entretien IA pour évaluer en profondeur les compétences de {candidate.first_name}
        </p>
        
       <button
  onClick={() => {
    if (!candidate.job_offer_id) {
      alert('❌ Erreur : Ce candidat n\'est pas associé à une offre d\'emploi')
      return
    }
    navigate(`/interviews?candidate=${candidate.id}&job=${candidate.job_offer_id}`)
  }}
  className="px-8 py-4 rounded-xl font-bold text-white shadow-2xl transition-all hover:scale-105 flex items-center gap-3 mx-auto text-lg"
  style={{ background: 'linear-gradient(135deg, #8D6CAB 0%, #007785 100%)' }}
>
  <MessageSquare className="w-6 h-6" strokeWidth={2.5} />
  Démarrer l'entretien IA
</button>
      </div>
    </div>
  )
}
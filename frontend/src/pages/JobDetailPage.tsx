import { useState } from 'react'
import { useNavigate, useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi, candidatesApi, linkedinApi } from '../services/api'
import { 
  ArrowLeft, Edit, Trash2, Users, TrendingUp, MapPin, Calendar, 
  DollarSign, Award, Download, Linkedin, Upload, Rocket, Copy, 
  CheckCircle, AlertCircle 
} from 'lucide-react'

export default function JobDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [showLinkedInPost, setShowLinkedInPost] = useState(false)
  const [linkedInPost, setLinkedInPost] = useState('')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [copied, setCopied] = useState(false)

  const { data: job, isLoading, isError, error } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.getById(Number(id)),
    retry: false,  // ✅ Ne pas réessayer si 404
  })

  const { data: candidates = [] } = useQuery({
    queryKey: ['candidates', id],
    queryFn: () => candidatesApi.getByJob(Number(id)),
    enabled: !!job,  // ✅ N'exécuter que si le job existe
  })

  // ✅ Vérifier si LinkedIn est connecté
  const { data: linkedinStatus } = useQuery({
    queryKey: ['linkedin-status'],
    queryFn: linkedinApi.getStatus,
    retry: false
  })

  const deleteMutation = useMutation({
    mutationFn: () => jobsApi.delete(Number(id)),
    onSuccess: () => {
      navigate('/jobs')
    },
  })

  const generateLinkedInMutation = useMutation({
    mutationFn: () => jobsApi.generateLinkedIn(Number(id)),
    onSuccess: (data) => {
      setLinkedInPost(data.linkedin_post)
      setShowLinkedInPost(true)
      queryClient.invalidateQueries({ queryKey: ['job', id] })
    },
    onError: (error: any) => {
      console.error('Erreur génération:', error)
      alert(`Erreur: ${error.response?.data?.detail || error.message}`)
    }
  })

  const publishMutation = useMutation({
    mutationFn: () => jobsApi.publishToLinkedIn(Number(id)),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['job', id] })
      setShowLinkedInPost(false)
      alert(`🎉 ${data.message}\n\nVotre annonce est maintenant visible sur LinkedIn !`)
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || error.message
      alert(`❌ Erreur publication : ${message}`)
    }
  })

  const handleGenerateLinkedIn = () => {
    generateLinkedInMutation.mutate()
  }

  const handlePublishToLinkedIn = () => {
    if (window.confirm('🚀 Publier cette annonce sur LinkedIn ?\n\nElle sera visible par votre réseau.')) {
      publishMutation.mutate()
    }
  }

  const handleExportExcel = async () => {
    try {
      const blob = await candidatesApi.exportExcel(Number(id))
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `candidates_${job?.title}.xlsx`
      a.click()
    } catch (error) {
      console.error('Export error:', error)
    }
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(linkedInPost)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

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

  // ✅ GESTION ERREUR 404
  if (isError || !job) {
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
            Offre introuvable
          </h2>
          
          <p className="mb-8 text-lg" style={{ color: '#888888' }}>
            L'offre d'emploi #{id} n'existe pas ou a été supprimée.
          </p>
          
          <button
            onClick={() => navigate('/jobs')}
            className="w-full px-6 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 flex items-center justify-center gap-2"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            <ArrowLeft className="w-5 h-5" strokeWidth={2.5} />
            Retour aux offres
          </button>
        </div>
      </div>
    )
  }

  const avgScore = candidates.length > 0
    ? candidates.reduce((sum: number, c: any) => sum + c.cv_score, 0) / candidates.length
    : 0

  const isLinkedInConnected = !!linkedinStatus

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
              onClick={() => navigate('/jobs')}
              className="w-12 h-12 rounded-xl backdrop-blur-xl flex items-center justify-center border transition-all hover:scale-110"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <ArrowLeft className="w-6 h-6 text-white" strokeWidth={2.5} />
            </button>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-5 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
                style={{ backgroundColor: 'white', color: '#007785' }}
              >
                <Upload className="w-5 h-5" strokeWidth={2.5} />
                Upload CV
              </button>
              <button
                onClick={handleGenerateLinkedIn}
                disabled={generateLinkedInMutation.isPending}
                className="px-5 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
                style={{ backgroundColor: 'white', color: '#0A66C2' }}
              >
                <Linkedin className="w-5 h-5" strokeWidth={2.5} />
                {generateLinkedInMutation.isPending ? 'Generating...' : 'LinkedIn Post'}
              </button>
              <button
                onClick={handleExportExcel}
                className="px-5 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
                style={{ backgroundColor: 'white', color: '#E68523' }}
              >
                <Download className="w-5 h-5" strokeWidth={2.5} />
                Export
              </button>
              <button
                onClick={() => navigate(`/jobs/edit/${id}`)}
                className="px-5 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
                style={{ backgroundColor: 'white', color: '#007785' }}
              >
                <Edit className="w-5 h-5" strokeWidth={2.5} />
                Edit
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-5 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105 flex items-center gap-2"
                style={{ backgroundColor: 'white', color: '#DD5143' }}
              >
                <Trash2 className="w-5 h-5" strokeWidth={2.5} />
                Delete
              </button>
            </div>
          </div>

          <h1 className="text-4xl font-bold text-white mb-4">{job.title}</h1>
          <div className="flex items-center gap-6 text-white/90">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5" strokeWidth={2} />
              <span>{job.location}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5" strokeWidth={2} />
              <span>{job.industry}</span>
            </div>
            {job.salary_min && job.salary_max && (
              <div className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" strokeWidth={2} />
                <span>{job.salary_min.toLocaleString()} - {job.salary_max.toLocaleString()} EUR</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-6">
        {[
          { label: 'Applications', value: (Array.isArray(candidates) ? candidates : []).length, icon: Users, color: '#007785' },
          { label: 'Avg Score', value: avgScore.toFixed(1), icon: TrendingUp, color: '#00ACDC' },
          { label: 'Top Grade', value: (Array.isArray(candidates) ? candidates : []).filter((c: any) => c.cv_score >= 80).length, icon: Award, color: '#E68523' }
        ].map((stat, idx) => (
          <div 
            key={idx}
            className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105"
            style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.8)',
              borderColor: 'rgba(202, 204, 206, 0.3)',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
            }}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-wider mb-1" style={{ color: '#888888' }}>{stat.label}</p>
                <p className="text-3xl font-bold" style={{ color: '#313335' }}>{stat.value}</p>
              </div>
              <div className="w-14 h-14 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${stat.color}15` }}>
                <stat.icon className="w-7 h-7" style={{ color: stat.color }} strokeWidth={2.5} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Job Details */}
      <div 
        className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <h2 className="text-2xl font-bold mb-4" style={{ color: '#313335' }}>Description</h2>
        <p className="mb-6" style={{ color: '#888888' }}>{job.description}</p>

        {job.responsibilities && (
          <>
            <h3 className="text-xl font-bold mb-3" style={{ color: '#313335' }}>Responsibilities</h3>
            <p className="mb-6" style={{ color: '#888888' }}>{job.responsibilities}</p>
          </>
        )}

        <h3 className="text-xl font-bold mb-3" style={{ color: '#313335' }}>Required Skills</h3>
        <div className="flex flex-wrap gap-2 mb-6">
          {(job.required_skills || []).map((skill: string, idx: number) => (
            <span key={idx} className="px-3 py-1.5 rounded-xl text-sm font-semibold" style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)', color: '#007785' }}>
              {skill}
            </span>
          ))}
        </div>

        {job.nice_to_have_skills && job.nice_to_have_skills.length > 0 && (
          <>
            <h3 className="text-xl font-bold mb-3" style={{ color: '#313335' }}>Nice to Have</h3>
            <div className="flex flex-wrap gap-2 mb-6">
              {job.nice_to_have_skills.map((skill: string, idx: number) => (
                <span key={idx} className="px-3 py-1.5 rounded-xl text-sm font-semibold" style={{ backgroundColor: 'rgba(141, 108, 171, 0.1)', color: '#8D6CAB' }}>
                  {skill}
                </span>
              ))}
            </div>
          </>
        )}

        {job.languages && job.languages.length > 0 && (
          <>
            <h3 className="text-xl font-bold mb-3" style={{ color: '#313335' }}>Languages</h3>
            <div className="flex flex-wrap gap-2">
              {job.languages.map((lang: any, idx: number) => (
                <span key={idx} className="px-3 py-1.5 rounded-xl text-sm font-semibold" style={{ backgroundColor: 'rgba(230, 133, 35, 0.1)', color: '#E68523' }}>
                  {lang.name} - {lang.level}
                </span>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Candidates List */}
      <div 
        className="backdrop-blur-xl rounded-2xl border shadow-xl overflow-hidden"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <div className="p-6 border-b" style={{ borderColor: 'rgba(202, 204, 206, 0.3)' }}>
          <h2 className="text-2xl font-bold" style={{ color: '#313335' }}>Candidates ({candidates.length})</h2>
        </div>

        {candidates.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="w-16 h-16 mx-auto mb-4" style={{ color: '#CACCCE' }} />
            <p className="text-lg font-semibold" style={{ color: '#888888' }}>No candidates yet</p>
          </div>
        ) : (
          <div className="divide-y" style={{ borderColor: 'rgba(202, 204, 206, 0.2)' }}>
            {candidates.map((candidate: any) => (
              <Link
                key={candidate.id}
                to={`/candidates/${candidate.id}`}
                className="flex items-center justify-between p-6 hover:bg-white/50 transition-all"
              >
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold shadow-lg"
                    style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                  >
                    {(candidate.first_name || 'U')[0]}{(candidate.last_name || '')[0]}
                  </div>
                  <div>
                    <p className="font-semibold" style={{ color: '#313335' }}>
                      {candidate.first_name} {candidate.last_name}
                    </p>
                    <p className="text-sm" style={{ color: '#888888' }}>{candidate.email}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-6">
                  <div className="text-right">
                    <p className="text-2xl font-bold" style={{ color: candidate.cv_score >= 80 ? '#007785' : candidate.cv_score >= 65 ? '#00ACDC' : '#E68523' }}>
                      {candidate.cv_score.toFixed(1)}
                    </p>
                    <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>Score</p>
                  </div>
                  <div className="w-16 h-2 rounded-full" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}>
                    <div 
                      className="h-full rounded-full"
                      style={{ 
                        width: `${candidate.cv_score}%`,
                        backgroundColor: candidate.cv_score >= 80 ? '#007785' : candidate.cv_score >= 65 ? '#00ACDC' : '#E68523'
                      }}
                    ></div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* MODAL LINKEDIN */}
      {showLinkedInPost && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
          <div 
            className="backdrop-blur-xl rounded-3xl p-8 border shadow-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col"
            style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
          >
            <div className="flex items-center justify-between mb-6 flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center"
                  style={{ background: 'linear-gradient(135deg, #0077B5 0%, #00A0DC 100%)' }}
                >
                  <Linkedin className="w-6 h-6 text-white" strokeWidth={2.5} />
                </div>
                <div>
                  <h2 className="text-2xl font-bold" style={{ color: '#313335' }}>
                    Annonce LinkedIn générée
                  </h2>
                  <p className="text-sm" style={{ color: '#888888' }}>
                    Prête à être publiée sur votre profil
                  </p>
                </div>
              </div>
              <button 
                onClick={() => setShowLinkedInPost(false)} 
                className="w-10 h-10 rounded-xl flex items-center justify-center transition-all hover:bg-gray-100"
                style={{ color: '#888888' }}
              >
                <span className="text-2xl">×</span>
              </button>
            </div>

            {!isLinkedInConnected && (
              <div className="mb-4 p-4 rounded-xl flex items-center gap-3 flex-shrink-0"
                style={{ backgroundColor: '#FEF2F2' }}
              >
                <AlertCircle className="w-5 h-5 flex-shrink-0" style={{ color: '#EF4444' }} />
                <div className="flex-1 min-w-0">
                  <p className="font-semibold" style={{ color: '#EF4444' }}>
                    LinkedIn non connecté
                  </p>
                  <p className="text-sm" style={{ color: '#888888' }}>
                    Connectez votre compte dans Settings pour publier automatiquement
                  </p>
                </div>
                <button
                  onClick={() => navigate('/settings')}
                  className="px-4 py-2 rounded-lg font-semibold text-white flex-shrink-0"
                  style={{ backgroundColor: '#0077B5' }}
                >
                  Settings
                </button>
              </div>
            )}

            <div className="flex-1 overflow-y-auto mb-6 min-h-0">
              <div 
                className="p-6 rounded-2xl border-2 border-dashed"
                style={{ 
                  backgroundColor: 'rgba(243, 242, 239, 0.5)',
                  borderColor: 'rgba(0, 119, 133, 0.2)'
                }}
              >
                <div className="flex items-start gap-3 mb-4">
                  <div 
                    className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold flex-shrink-0"
                    style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                  >
                    {linkedinStatus?.first_name?.[0] || 'U'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold" style={{ color: '#313335' }}>
                      {linkedinStatus?.first_name} {linkedinStatus?.last_name}
                    </p>
                    <p className="text-sm flex items-center gap-1" style={{ color: '#888888' }}>
                      <span>À l'instant</span>
                      <span>•</span>
                      <span>🌐</span>
                    </p>
                  </div>
                </div>

                <div 
                  className="whitespace-pre-wrap font-sans leading-relaxed"
                  style={{ color: '#313335', fontSize: '15px' }}
                >
                  {linkedInPost}
                </div>

                <div className="mt-4 pt-4 border-t flex items-center gap-6 text-sm"
                  style={{ borderColor: 'rgba(202, 204, 206, 0.3)', color: '#888888' }}
                >
                  <div className="flex items-center gap-2">
                    <span>👍</span>
                    <span>J'aime</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>💬</span>
                    <span>Commenter</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>🔄</span>
                    <span>Partager</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 mt-4">
                <div className="p-3 rounded-xl text-center"
                  style={{ backgroundColor: 'rgba(0, 119, 133, 0.05)' }}
                >
                  <p className="text-2xl font-bold" style={{ color: '#007785' }}>
                    {linkedInPost.length}
                  </p>
                  <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>
                    Caractères
                  </p>
                </div>
                <div className="p-3 rounded-xl text-center"
                  style={{ backgroundColor: 'rgba(0, 172, 220, 0.05)' }}
                >
                  <p className="text-2xl font-bold" style={{ color: '#00ACDC' }}>
                    {linkedInPost.split('\n\n').length}
                  </p>
                  <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>
                    Paragraphes
                  </p>
                </div>
                <div className="p-3 rounded-xl text-center"
                  style={{ backgroundColor: 'rgba(230, 133, 35, 0.05)' }}
                >
                  <p className="text-2xl font-bold" style={{ color: '#E68523' }}>
                    {(linkedInPost.match(/#/g) || []).length}
                  </p>
                  <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>
                    Hashtags
                  </p>
                </div>
              </div>
            </div>

            <div className="flex gap-3 flex-shrink-0">
              <button
                onClick={copyToClipboard}
                className="flex-1 px-6 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 flex items-center justify-center gap-2"
                style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
              >
                {copied ? (
                  <>
                    <CheckCircle className="w-5 h-5" strokeWidth={2.5} />
                    Copié !
                  </>
                ) : (
                  <>
                    <Copy className="w-5 h-5" strokeWidth={2.5} />
                    Copier
                  </>
                )}
              </button>

              <button
                onClick={handlePublishToLinkedIn}
                disabled={publishMutation.isPending || !isLinkedInConnected}
                className="flex-1 px-6 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ 
                  background: isLinkedInConnected 
                    ? 'linear-gradient(135deg, #0077B5 0%, #00A0DC 100%)' 
                    : '#88888850'
                }}
                title={!isLinkedInConnected ? 'Connectez LinkedIn d\'abord' : ''}
              >
                {publishMutation.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Publication...
                  </>
                ) : (
                  <>
                    <Rocket className="w-5 h-5" strokeWidth={2.5} />
                    Publier sur LinkedIn
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
          <div 
            className="backdrop-blur-xl rounded-3xl p-8 border shadow-2xl max-w-md w-full"
            style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
          >
            <h2 className="text-2xl font-bold mb-4" style={{ color: '#313335' }}>Delete Job?</h2>
            <p className="mb-6" style={{ color: '#888888' }}>Are you sure you want to delete this job? This action cannot be undone.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 px-6 py-3 rounded-xl font-semibold transition-all hover:scale-105"
                style={{ backgroundColor: 'rgba(136, 136, 136, 0.1)', color: '#888888' }}
              >
                Cancel
              </button>
              <button
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
                className="flex-1 px-6 py-3 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105"
                style={{ background: 'linear-gradient(135deg, #DD5143 0%, #E68523 100%)' }}
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload CV Modal */}
      {showUploadModal && (
        <UploadCVModal
          jobId={Number(id)}
          onClose={() => {
            setShowUploadModal(false)
            queryClient.invalidateQueries({ queryKey: ['candidates', id] })
          }}
        />
      )}
    </div>
  )
}

// ✅ Upload CV Modal Component
function UploadCVModal({ jobId, onClose }: { jobId: number; onClose: () => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleUpload = async () => {
    if (!file) {
      setError('Veuillez sélectionner un fichier')
      return
    }

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain'
    ]
    
    if (!allowedTypes.includes(file.type)) {
      setError('Type de fichier non supporté. Utilisez PDF, DOC, DOCX ou TXT')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('Fichier trop volumineux (max 10MB)')
      return
    }

    setUploading(true)
    setError(null)

    try {
      console.log('📤 Upload du CV...')
      console.log('   Fichier:', file.name)
      console.log('   Type:', file.type)
      console.log('   Taille:', (file.size / 1024).toFixed(2), 'KB')
      console.log('   Job ID:', jobId)

      await candidatesApi.uploadCV(file, jobId)
      
      console.log('✅ CV uploadé avec succès !')
      alert('✅ CV uploadé et analysé avec succès !\n\nLe candidat a été ajouté à la liste.')
      onClose()
    } catch (error: any) {
      console.error('❌ Erreur upload:', error)
      console.error('   Response:', error.response)
      
      let errorMessage = 'Échec de l\'upload'
      
      if (error.response?.data?.detail) {
        if (typeof error.response.data.detail === 'string') {
          errorMessage = error.response.data.detail
        } else if (Array.isArray(error.response.data.detail)) {
          errorMessage = error.response.data.detail
            .map((e: any) => `${e.loc?.join('.') || 'Erreur'}: ${e.msg}`)
            .join('\n')
        } else if (typeof error.response.data.detail === 'object') {
          errorMessage = JSON.stringify(error.response.data.detail)
        }
      } else if (error.message) {
        errorMessage = error.message
      }
      
      console.error('   Message:', errorMessage)
      setError(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[9999] p-4">
      <div 
        className="backdrop-blur-xl rounded-3xl p-8 border shadow-2xl max-w-md w-full"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            <Upload className="w-6 h-6 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <h2 className="text-2xl font-bold" style={{ color: '#313335' }}>
              Upload CV
            </h2>
            <p className="text-sm" style={{ color: '#888888' }}>
              Analyse automatique avec IA
            </p>
          </div>
        </div>
        
        <div className="mb-6">
          <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>
            Sélectionner un fichier CV
          </label>
          <input
            type="file"
            accept=".pdf,.doc,.docx,.txt"
            onChange={(e) => {
              setFile(e.target.files?.[0] || null)
              setError(null)
            }}
            disabled={uploading}
            className="w-full px-4 py-3 rounded-xl border transition-all"
            style={{ 
              backgroundColor: 'rgba(243, 242, 239, 0.5)', 
              borderColor: 'rgba(202, 204, 206, 0.3)', 
              color: '#313335',
              cursor: uploading ? 'not-allowed' : 'pointer'
            }}
          />
          
          {file && (
            <div className="mt-3 p-3 rounded-xl" style={{ backgroundColor: 'rgba(0, 119, 133, 0.05)' }}>
              <div className="flex items-center gap-2">
                <span className="text-2xl">📄</span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold truncate" style={{ color: '#007785' }}>
                    {file.name}
                  </p>
                  <p className="text-xs" style={{ color: '#888888' }}>
                    {(file.size / 1024).toFixed(2)} KB • {file.type.split('/')[1]?.toUpperCase() || 'Fichier'}
                  </p>
                </div>
              </div>
            </div>
          )}
          
          <p className="mt-2 text-xs" style={{ color: '#888888' }}>
            Formats acceptés : PDF, DOC, DOCX, TXT (max 10MB)
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl flex items-start gap-3"
            style={{ backgroundColor: '#FEF2F2' }}
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: '#EF4444' }} />
            <div className="flex-1 min-w-0">
              <p className="font-semibold" style={{ color: '#EF4444' }}>
                Erreur d'upload
              </p>
              <p className="text-sm whitespace-pre-wrap" style={{ color: '#888888' }}>
                {error}
              </p>
            </div>
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={onClose}
            disabled={uploading}
            className="flex-1 px-6 py-3 rounded-xl font-semibold transition-all hover:scale-105 disabled:opacity-50"
            style={{ backgroundColor: 'rgba(136, 136, 136, 0.1)', color: '#888888' }}
          >
            Annuler
          </button>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="flex-1 px-6 py-3 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 disabled:opacity-50 flex items-center justify-center gap-2"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Upload...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" strokeWidth={2.5} />
                Upload
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
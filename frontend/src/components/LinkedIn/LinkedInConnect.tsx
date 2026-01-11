import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Linkedin, CheckCircle, ExternalLink, AlertCircle } from 'lucide-react'
import { linkedinApi } from '../../services/api'

export default function LinkedInConnect() {
  const queryClient = useQueryClient()
  const [connecting, setConnecting] = useState(false)

  // Vérifier le statut de connexion
  const { data: status, isLoading, error } = useQuery({
    queryKey: ['linkedin-status'],
    queryFn: linkedinApi.getStatus,
    retry: false,
    // ✅ AJOUT : Ne pas considérer 404 comme une erreur
    throwOnError: false
  })

  // Déconnexion
  const disconnectMutation = useMutation({
    mutationFn: linkedinApi.disconnect,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['linkedin-status'] })
      alert('✅ Compte LinkedIn déconnecté')
    },
    onError: (error: any) => {
      alert(`❌ Erreur : ${error.message}`)
    }
  })

  const handleConnect = async () => {
    setConnecting(true)
    try {
      const { authorization_url } = await linkedinApi.getConnectUrl()
      // Rediriger vers LinkedIn OAuth
      window.location.href = authorization_url
    } catch (error: any) {
      console.error('Erreur connexion:', error)
      alert(`❌ Erreur : ${error.message}`)
      setConnecting(false)
    }
  }

  const isConnected = !!status

  // ✅ État de chargement
  if (isLoading) {
    return (
      <div 
        className="backdrop-blur-xl rounded-2xl p-6 border"
        style={{ 
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderColor: 'rgba(202, 204, 206, 0.3)'
        }}
      >
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span style={{ color: '#888888' }}>Loading LinkedIn status...</span>
        </div>
      </div>
    )
  }

  return (
    <div 
      className="backdrop-blur-xl rounded-2xl p-6 border"
      style={{ 
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        borderColor: 'rgba(202, 204, 206, 0.3)'
      }}
    >
      <div className="flex items-start gap-4">
        <div 
          className="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0"
          style={{ backgroundColor: '#0077B515' }}
        >
          <Linkedin className="w-7 h-7" style={{ color: '#0077B5' }} strokeWidth={2.5} />
        </div>

        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-bold" style={{ color: '#313335' }}>
              LinkedIn Integration
            </h3>
            {isConnected && (
              <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg"
                style={{ backgroundColor: '#10B98115' }}
              >
                <CheckCircle className="w-4 h-4" style={{ color: '#10B981' }} strokeWidth={2.5} />
                <span className="text-xs font-bold" style={{ color: '#10B981' }}>Connected</span>
              </div>
            )}
          </div>

          <p className="text-sm mb-4" style={{ color: '#888888' }}>
            {isConnected 
              ? `Connected as ${status?.first_name || ''} ${status?.last_name || ''} (${status?.email || ''})`
              : 'Connect your LinkedIn account to automatically publish job offers'
            }
          </p>

          {/* ✅ Afficher les erreurs éventuelles */}
          {error && !isConnected && (
            <div className="flex items-center gap-2 mb-4 p-3 rounded-lg"
              style={{ backgroundColor: '#FEF2F2' }}
            >
              <AlertCircle className="w-4 h-4" style={{ color: '#EF4444' }} />
              <span className="text-sm" style={{ color: '#EF4444' }}>
                Not connected to LinkedIn
              </span>
            </div>
          )}

          {isConnected ? (
            <div className="flex gap-3">
              <button
                onClick={() => window.open('https://www.linkedin.com/feed', '_blank')}
                className="flex items-center gap-2 px-4 py-2 rounded-xl font-semibold transition-all hover:scale-105"
                style={{ backgroundColor: '#0077B515', color: '#0077B5' }}
              >
                <ExternalLink className="w-4 h-4" strokeWidth={2.5} />
                View Profile
              </button>
              <button
                onClick={() => disconnectMutation.mutate()}
                disabled={disconnectMutation.isPending}
                className="px-4 py-2 rounded-xl font-semibold transition-all hover:scale-105"
                style={{ backgroundColor: '#EF444415', color: '#EF4444' }}
              >
                {disconnectMutation.isPending ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </div>
          ) : (
            <button
              onClick={handleConnect}
              disabled={connecting}
              className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white transition-all hover:scale-105 shadow-lg"
              style={{ backgroundColor: '#0077B5' }}
            >
              <Linkedin className="w-5 h-5" strokeWidth={2.5} />
              {connecting ? 'Connecting...' : 'Connect LinkedIn Account'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
import { Settings as SettingsIcon } from 'lucide-react'
import LinkedInConnect from '../components/LinkedIn/LinkedInConnect'

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div 
        className="relative overflow-hidden rounded-3xl p-8 shadow-2xl"
        style={{ background: 'linear-gradient(135deg, #8D6CAB 0%, #007785 100%)' }}
      >
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}></div>
        </div>
        
        <div className="relative flex items-center gap-5">
          <div className="w-16 h-16 rounded-2xl backdrop-blur-xl flex items-center justify-center border"
            style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              borderColor: 'rgba(255, 255, 255, 0.2)'
            }}
          >
            <SettingsIcon className="w-8 h-8 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Settings</h1>
            <p className="text-white/80 text-base">Manage your integrations and preferences</p>
          </div>
        </div>
      </div>

      {/* Integrations Section */}
      <div>
        <h2 className="text-xl font-bold mb-4" style={{ color: '#313335' }}>
          Integrations
        </h2>
        
        {/* LinkedIn Integration */}
        <LinkedInConnect />
      </div>

      {/* Future sections */}
      <div>
        <h2 className="text-xl font-bold mb-4" style={{ color: '#313335' }}>
          General Settings
        </h2>
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            borderColor: 'rgba(202, 204, 206, 0.3)'
          }}
        >
          <p style={{ color: '#888888' }}>More settings coming soon...</p>
        </div>
      </div>
    </div>
  )
}
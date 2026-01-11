import { Send } from 'lucide-react'

interface ResponseInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  loading: boolean
}

export default function ResponseInput({ value, onChange, onSend, loading }: ResponseInputProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div 
      className="backdrop-blur-xl rounded-2xl p-4 border shadow-xl"
      style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
    >
      <div className="flex gap-3">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Write your response here... (Shift+Enter for new line)"
          className="flex-1 px-4 py-3 rounded-xl border resize-none"
          style={{ 
            backgroundColor: 'rgba(243, 242, 239, 0.5)', 
            borderColor: 'rgba(202, 204, 206, 0.3)',
            color: '#313335'
          }}
          rows={4}
          disabled={loading}
        />
        <button
          onClick={onSend}
          disabled={loading || !value.trim()}
          className="px-6 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
        >
          <Send className="w-5 h-5" strokeWidth={2.5} />
          Send
        </button>
      </div>
    </div>
  )
}
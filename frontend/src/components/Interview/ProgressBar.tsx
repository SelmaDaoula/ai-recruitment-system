interface ProgressBarProps {
  current: number
  total: number
}

export default function ProgressBar({ current, total }: ProgressBarProps) {
  const percentage = (current / total) * 100

  return (
    <div>
      <div className="flex justify-between text-sm mb-2" style={{ color: '#313335' }}>
        <span className="font-semibold">Question {current} of {total}</span>
        <span className="font-bold" style={{ color: '#007785' }}>{percentage.toFixed(0)}%</span>
      </div>
      <div className="h-3 rounded-full" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}>
        <div
          className="h-3 rounded-full transition-all duration-500"
          style={{ 
            width: `${percentage}%`,
            background: 'linear-gradient(90deg, #007785 0%, #00ACDC 100%)'
          }}
        />
      </div>
    </div>
  )
}
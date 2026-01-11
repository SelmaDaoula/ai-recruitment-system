import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { statsApi, jobsApi, candidatesApi } from '../services/api'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Users, Briefcase, TrendingUp, Award, ArrowUpRight, MapPin, Calendar, Star } from 'lucide-react'

export default function DashboardPage() {
  const { data: globalStats, isLoading: statsLoading } = useQuery({
    queryKey: ['globalStats'],
    queryFn: () => statsApi.getGlobalStats(),  // ✅ Arrow function
  })

  const { data: jobs = [], isLoading: jobsLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.getAll(),  // ✅ Arrow function
  })

  const { data: candidates = [], isLoading: candidatesLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => candidatesApi.getAll(),  // ✅ Arrow function
  })

  const isLoading = statsLoading || jobsLoading || candidatesLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[70vh]">
        <div className="relative w-16 h-16">
          <div className="absolute inset-0 rounded-full" style={{ border: '4px solid #CACCCE' }}></div>
          <div 
            className="absolute inset-0 rounded-full animate-spin"
            style={{ border: '4px solid #007785', borderTopColor: 'transparent' }}
          ></div>
        </div>
      </div>
    )
  }

  const scoreDistribution = [
    { name: 'Excellent', value: globalStats?.quality_distribution?.excellent || 0, color: '#007785' },
    { name: 'Good', value: globalStats?.quality_distribution?.good || 0, color: '#00ACDC' },
    { name: 'Average', value: globalStats?.quality_distribution?.average || 0, color: '#E68523' },
    { name: 'Poor', value: globalStats?.quality_distribution?.poor || 0, color: '#888888' },
  ]

  // Ensure data are arrays
  const jobsArray = Array.isArray(jobs) ? jobs : []
  const candidatesArray = Array.isArray(candidates) ? candidates : []

  const jobsData = jobsArray.slice(0, 6).map((job: any) => ({
    name: job.title?.substring(0, 12) || 'Job',
    value: candidatesArray.filter((c: any) => c.job_offer_id === job.id).length
  }))

  const topPerformers = [...candidatesArray]
    .sort((a: any, b: any) => (b.cv_score || 0) - (a.cv_score || 0))
    .slice(0, 5)

  function getCategoryColor(score: number): string {
    if (score >= 80) return '#007785'
    if (score >= 65) return '#00ACDC'
    if (score >= 50) return '#E68523'
    return '#888888'
  }

  return (
    <div className="space-y-6">
      {/* Header Hero */}
      <div 
        className="relative overflow-hidden rounded-3xl p-8 shadow-2xl"
        style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
      >
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}></div>
        </div>
        
        <div className="relative">
          <div className="flex items-center space-x-5 mb-6">
            <div className="w-16 h-16 rounded-2xl backdrop-blur-xl flex items-center justify-center border"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <TrendingUp className="w-8 h-8 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Recruitment Dashboard</h1>
              <p className="text-white/80 text-base">AI-Powered Candidate Analysis • ML Accuracy 99.96%</p>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="backdrop-blur-xl rounded-2xl p-4 border"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <p className="text-white/70 text-sm font-semibold mb-1">Active Users</p>
              <p className="text-2xl font-bold text-white">247</p>
            </div>
            <div className="backdrop-blur-xl rounded-2xl p-4 border"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <p className="text-white/70 text-sm font-semibold mb-1">Response Rate</p>
              <p className="text-2xl font-bold text-white">94%</p>
            </div>
            <div className="backdrop-blur-xl rounded-2xl p-4 border"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <p className="text-white/70 text-sm font-semibold mb-1">Avg Time to Hire</p>
              <p className="text-2xl font-bold text-white">12 days</p>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: 'Total Jobs', value: jobs.length, icon: Briefcase, color: '#007785' },
          { label: 'Total Candidates', value: candidates.length, icon: Users, color: '#00ACDC' },
          { label: 'Average Score', value: globalStats?.average_score?.toFixed(1) || '0.0', icon: TrendingUp, color: '#E68523' },
          { label: 'Grade A', value: candidatesArray.filter((c: any) => c.cv_score >= 80).length, icon: Award, color: '#8D6CAB' }
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
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#888888' }}>{stat.label}</p>
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${stat.color}15` }}>
                <stat.icon className="w-5 h-5" style={{ color: stat.color }} strokeWidth={2.5} />
              </div>
            </div>
            <p className="text-3xl font-bold" style={{ color: '#313335' }}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Top Performers - Replaces Weekly Activity */}
      <div 
        className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <h2 className="text-2xl font-bold mb-6" style={{ color: '#313335' }}>Top 5 Performers</h2>
        
        {topPerformers.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-16 h-16 mx-auto mb-4" style={{ color: '#CACCCE' }} />
            <p className="text-lg font-semibold" style={{ color: '#888888' }}>No candidates yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {topPerformers.map((candidate: any, idx: number) => {
              const score = candidate.cv_score || 0
              const color = getCategoryColor(score)
              
              return (
                <Link
                  key={candidate.id}
                  to={`/candidates/${candidate.id}`}
                  className="flex items-center justify-between p-4 rounded-xl transition-all hover:scale-105"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)' }}
                >
                  <div className="flex items-center space-x-4">
                    {idx === 0 && (
                      <Star className="w-6 h-6 fill-current" style={{ color: '#E68523' }} />
                    )}
                    <div 
                      className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold shadow-lg"
                      style={{ background: `linear-gradient(135deg, ${color} 0%, #007785 100%)` }}
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

                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-2xl font-bold" style={{ color }}>
                        {score.toFixed(1)}
                      </p>
                      <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: '#888888' }}>Score</p>
                    </div>
                    <div className="w-24 h-2 rounded-full" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}>
                      <div 
                        className="h-full rounded-full transition-all"
                        style={{ width: `${score}%`, backgroundColor: color }}
                      ></div>
                    </div>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Distribution Chart */}
        <div 
          className="col-span-4 backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <h2 className="text-2xl font-bold mb-6" style={{ color: '#313335' }}>Distribution</h2>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={scoreDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
              >
                {scoreDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-2 mt-6">
            {scoreDistribution.map((item, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                <span className="text-sm font-medium" style={{ color: '#313335' }}>
                  {item.name} ({item.value})
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Job Performance Chart */}
        <div 
          className="col-span-8 backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <h2 className="text-2xl font-bold mb-6" style={{ color: '#313335' }}>Job Performance</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={jobsData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(202, 204, 206, 0.3)" />
              <XAxis dataKey="name" stroke="#888888" style={{ fontSize: '12px' }} />
              <YAxis stroke="#888888" style={{ fontSize: '12px' }} />
              <Tooltip />
              <Bar dataKey="value" radius={[10, 10, 0, 0]}>
                {jobsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#007785' : '#00ACDC'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Positions */}
      <div 
        className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <h2 className="text-2xl font-bold mb-6" style={{ color: '#313335' }}>Recent Positions</h2>
        <div className="grid grid-cols-3 gap-6">
          {jobsArray.slice(0, 6).map((job: any) => {
            const jobCandidates = candidatesArray.filter((c: any) => c.job_offer_id === job.id)
            const avgScore = jobCandidates.length > 0
              ? jobCandidates.reduce((sum: number, c: any) => sum + c.cv_score, 0) / jobCandidates.length
              : 0

            return (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
              >
                <div className="flex items-center justify-between mb-4">
                  <Briefcase className="w-8 h-8" style={{ color: '#007785' }} strokeWidth={2} />
                  <span 
                    className="px-3 py-1 rounded-full text-xs font-bold"
                    style={{ 
                      backgroundColor: job.is_active ? 'rgba(0, 119, 133, 0.1)' : 'rgba(136, 136, 136, 0.1)',
                      color: job.is_active ? '#007785' : '#888888'
                    }}
                  >
                    {job.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <h3 className="text-lg font-bold mb-2" style={{ color: '#313335' }}>{job.title}</h3>
                <div className="flex items-center space-x-2 mb-2">
                  <MapPin className="w-4 h-4" style={{ color: '#888888' }} strokeWidth={2} />
                  <span className="text-sm" style={{ color: '#888888' }}>{job.location}</span>
                </div>
                <div className="flex items-center space-x-2 mb-4">
                  <Calendar className="w-4 h-4" style={{ color: '#888888' }} strokeWidth={2} />
                  <span className="text-sm" style={{ color: '#888888' }}>
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'rgba(202, 204, 206, 0.3)' }}>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" style={{ color: '#007785' }} strokeWidth={2} />
                    <span className="text-sm font-semibold" style={{ color: '#007785' }}>
                      {jobCandidates.length} candidates
                    </span>
                  </div>
                  {avgScore > 0 && (
                    <span className="text-sm font-bold" style={{ color: '#E68523' }}>
                      {avgScore.toFixed(1)} avg
                    </span>
                  )}
                </div>
              </Link>
            )
          })}
        </div>
      </div>
    </div>
  )
}
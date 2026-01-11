import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { jobsApi, candidatesApi } from '../services/api'
import { Briefcase, MapPin, Users, TrendingUp, Search, Plus, DollarSign, Building2, Code, Laptop } from 'lucide-react'

export default function JobsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all')

  // ✅ CORRECTION : Wrapper avec une arrow function
  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.getAll(),
  })

  // ✅ CORRECTION : Wrapper avec une arrow function
  const { data: candidates = [] } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => candidatesApi.getAll(),
  })

  const filteredJobs = jobs.filter((job: any) => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (job.location || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (job.industry || '').toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'active' && job.is_active) ||
                         (filterStatus === 'inactive' && !job.is_active)
    
    return matchesSearch && matchesStatus
  })

  const jobIcons = [Building2, Code, Laptop, Briefcase, Users, TrendingUp]

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

  return (
    <div className="space-y-6">
      {/* Modern Hero */}
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
        
        <div className="relative flex items-center justify-between">
          <div className="flex items-center space-x-5">
            <div className="w-16 h-16 rounded-2xl backdrop-blur-xl flex items-center justify-center border"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <Briefcase className="w-8 h-8 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Job Opportunities</h1>
              <p className="text-white/80 text-base">Manage and track all your job positions</p>
            </div>
          </div>

          <Link
            to="/jobs/create"
            className="px-6 py-3 rounded-xl font-semibold text-sm shadow-xl transition-all hover:scale-105 flex items-center space-x-2"
            style={{ backgroundColor: 'white', color: '#007785' }}
          >
            <Plus className="w-5 h-5" strokeWidth={2.5} />
            <span>New Job</span>
          </Link>
        </div>
      </div>

      {/* Search & Filter */}
      <div 
        className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <div className="flex items-center justify-between gap-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: '#888888' }} strokeWidth={2} />
            <input
              type="text"
              placeholder="Search jobs by title, location, or industry..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border"
              style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
            />
          </div>

          <div className="flex items-center gap-2">
            {(['all', 'active', 'inactive'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className="px-4 py-2 rounded-xl font-semibold text-sm transition-all capitalize"
                style={{
                  backgroundColor: filterStatus === status ? 'rgba(0, 119, 133, 0.1)' : 'transparent',
                  color: filterStatus === status ? '#007785' : '#888888'
                }}
              >
                {status}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Jobs Grid */}
      {filteredJobs.length === 0 ? (
        <div 
          className="backdrop-blur-xl rounded-2xl p-12 border text-center"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <Briefcase className="w-16 h-16 mx-auto mb-4" style={{ color: '#CACCCE' }} />
          <h3 className="text-xl font-bold mb-2" style={{ color: '#313335' }}>
            {searchTerm || filterStatus !== 'all' ? 'No jobs match your filters' : 'No jobs yet'}
          </h3>
          <p className="mb-6" style={{ color: '#888888' }}>
            {searchTerm || filterStatus !== 'all' 
              ? 'Try adjusting your search or filters' 
              : 'Get started by creating your first job posting'}
          </p>
          {!searchTerm && filterStatus === 'all' && (
            <Link
              to="/jobs/create"
              className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl font-semibold shadow-xl transition-all hover:scale-105"
              style={{ backgroundColor: '#007785', color: 'white' }}
            >
              <Plus className="w-5 h-5" strokeWidth={2.5} />
              <span>Create First Job</span>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          {filteredJobs.map((job: any, index: number) => {
            const Icon = jobIcons[index % jobIcons.length]
            const candidatesArray = Array.isArray(candidates) ? candidates : []
            const jobCandidates = candidatesArray.filter((c: any) => c.job_offer_id === job.id)
            const avgScore = jobCandidates.length > 0
              ? jobCandidates.reduce((sum: number, c: any) => sum + c.cv_score, 0) / jobCandidates.length
              : 0

            return (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105 hover:-translate-y-1"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  borderColor: 'rgba(202, 204, 206, 0.3)',
                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
                }}
              >
                <div className="flex items-start justify-between mb-4">
                  <div 
                    className="w-14 h-14 rounded-xl flex items-center justify-center shadow-lg"
                    style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                  >
                    <Icon className="w-7 h-7 text-white" strokeWidth={2.5} />
                  </div>
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

                <h3 className="text-xl font-bold mb-3" style={{ color: '#313335' }}>{job.title}</h3>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4" style={{ color: '#888888' }} strokeWidth={2} />
                    <span className="text-sm" style={{ color: '#888888' }}>{job.location}</span>
                  </div>
                  {job.salary_min && job.salary_max && (
                    <div className="flex items-center space-x-2">
                      <DollarSign className="w-4 h-4" style={{ color: '#888888' }} strokeWidth={2} />
                      <span className="text-sm" style={{ color: '#888888' }}>
                        {job.salary_min.toLocaleString()} - {job.salary_max.toLocaleString()} EUR
                      </span>
                    </div>
                  )}
                </div>

                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {job.required_skills.slice(0, 3).map((skill: string, idx: number) => (
                      <span 
                        key={idx}
                        className="px-2 py-1 rounded-lg text-xs font-semibold"
                        style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)', color: '#007785' }}
                      >
                        {skill}
                      </span>
                    ))}
                    {job.required_skills.length > 3 && (
                      <span 
                        className="px-2 py-1 rounded-lg text-xs font-semibold"
                        style={{ backgroundColor: 'rgba(141, 108, 171, 0.1)', color: '#8D6CAB' }}
                      >
                        +{job.required_skills.length - 3}
                      </span>
                    )}
                  </div>
                )}

                <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'rgba(202, 204, 206, 0.3)' }}>
                  <div className="flex items-center space-x-1">
                    <Users className="w-4 h-4" style={{ color: '#007785' }} strokeWidth={2} />
                    <span className="text-sm font-semibold" style={{ color: '#007785' }}>
                      {jobCandidates.length} {jobCandidates.length === 1 ? 'candidate' : 'candidates'}
                    </span>
                  </div>
                  {avgScore > 0 && (
                    <div className="flex items-center space-x-1">
                      <TrendingUp className="w-4 h-4" style={{ color: '#E68523' }} strokeWidth={2} />
                      <span className="text-sm font-bold" style={{ color: '#E68523' }}>
                        {avgScore.toFixed(1)} avg
                      </span>
                    </div>
                  )}
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
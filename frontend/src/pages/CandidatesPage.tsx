import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { candidatesApi, statsApi } from '../services/api'
import { Users, Search, Award, TrendingUp, ArrowUpDown } from 'lucide-react'

type SortField = 'name' | 'score' | 'date'
type SortOrder = 'asc' | 'desc'

export default function CandidatesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState<'all' | 'A' | 'B' | 'C' | 'D'>('all')
  const [sortField, setSortField] = useState<SortField>('score')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')

  // ✅ CORRECTION : Wrapper avec une arrow function
  const { data: candidates = [], isLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: () => candidatesApi.getAll(),
  })

  // ✅ CORRECTION : Wrapper avec une arrow function
  const { data: globalStats } = useQuery({
    queryKey: ['globalStats'],
    queryFn: () => statsApi.getGlobalStats(),
  })

  const getCategory = (score: number): string => {
    if (score >= 80) return 'A'
    if (score >= 65) return 'B'
    if (score >= 50) return 'C'
    return 'D'
  }

  const getCategoryColor = (category: string): string => {
    if (category === 'A') return '#007785'
    if (category === 'B') return '#00ACDC'
    if (category === 'C') return '#E68523'
    return '#888888'
  }

  // Ensure candidates is an array
  const candidatesArray = Array.isArray(candidates) ? candidates : []

  const filteredCandidates = candidatesArray
    .filter((candidate: any) => {
      const fullName = `${candidate.first_name || ''} ${candidate.last_name || ''}`.toLowerCase()
      const matchesSearch = fullName.includes(searchTerm.toLowerCase()) ||
                           (candidate.email || '').toLowerCase().includes(searchTerm.toLowerCase())
      
      const category = getCategory(candidate.cv_score || 0)
      const matchesCategory = filterCategory === 'all' || category === filterCategory
      
      return matchesSearch && matchesCategory
    })
    .sort((a: any, b: any) => {
      let comparison = 0
      
      if (sortField === 'score') {
        comparison = (a.cv_score || 0) - (b.cv_score || 0)
      } else if (sortField === 'name') {
        const nameA = `${a.first_name || ''} ${a.last_name || ''}`
        const nameB = `${b.first_name || ''} ${b.last_name || ''}`
        comparison = nameA.localeCompare(nameB)
      } else if (sortField === 'date') {
        const dateA = new Date(a.created_at || 0).getTime()
        const dateB = new Date(b.created_at || 0).getTime()
        comparison = dateA - dateB
      }
      
      return sortOrder === 'asc' ? comparison : -comparison
    })

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

  const totalCandidates = candidatesArray.length
  const gradeACandidates = candidatesArray.filter((c: any) => (c.cv_score || 0) >= 80).length
  const avgScore = globalStats?.average_score?.toFixed(1) || '0.0'
  const pendingCandidates = candidatesArray.filter((c: any) => c.application_status === 'pending').length

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
      {/* Header */}
      <div 
        className="relative overflow-hidden rounded-3xl p-8 shadow-2xl"
        style={{ background: 'linear-gradient(135deg, #00ACDC 0%, #007785 100%)' }}
      >
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
            backgroundSize: '32px 32px'
          }}></div>
        </div>
        
        <div className="relative flex items-center space-x-5">
          <div className="w-16 h-16 rounded-2xl backdrop-blur-xl flex items-center justify-center border"
            style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.15)',
              borderColor: 'rgba(255, 255, 255, 0.2)'
            }}
          >
            <Users className="w-8 h-8 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Candidates</h1>
            <p className="text-white/80 text-base">AI-analyzed candidates with ML scoring</p>
          </div>
        </div>
      </div>
  

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#888888' }}>Total Candidates</p>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: 'rgba(0, 119, 133, 0.15)' }}>
              <Users className="w-5 h-5" style={{ color: '#007785' }} strokeWidth={2.5} />
            </div>
          </div>
          <p className="text-3xl font-bold" style={{ color: '#313335' }}>{totalCandidates}</p>
        </div>

        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#888888' }}>Grade A</p>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: 'rgba(0, 172, 220, 0.15)' }}>
              <Award className="w-5 h-5" style={{ color: '#00ACDC' }} strokeWidth={2.5} />
            </div>
          </div>
          <p className="text-3xl font-bold" style={{ color: '#313335' }}>{gradeACandidates}</p>
        </div>

        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#888888' }}>Average Score</p>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: 'rgba(230, 133, 35, 0.15)' }}>
              <TrendingUp className="w-5 h-5" style={{ color: '#E68523' }} strokeWidth={2.5} />
            </div>
          </div>
          <p className="text-3xl font-bold" style={{ color: '#313335' }}>{avgScore}</p>
        </div>

        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border transition-all hover:scale-105"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            borderColor: 'rgba(202, 204, 206, 0.3)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.06)'
          }}
        >
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-semibold uppercase tracking-wider" style={{ color: '#888888' }}>Pending</p>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: 'rgba(141, 108, 171, 0.15)' }}>
              <Users className="w-5 h-5" style={{ color: '#8D6CAB' }} strokeWidth={2.5} />
            </div>
          </div>
          <p className="text-3xl font-bold" style={{ color: '#313335' }}>{pendingCandidates}</p>
        </div>
      </div>

      {/* Search & Filters */}
      <div 
        className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <div className="flex items-center justify-between gap-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: '#888888' }} strokeWidth={2} />
            <input
              type="text"
              placeholder="Search candidates by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border"
              style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
            />
          </div>

          <div className="flex items-center gap-2">
            {(['all', 'A', 'B', 'C', 'D'] as const).map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className="px-4 py-2 rounded-xl font-semibold text-sm transition-all"
                style={{
                  backgroundColor: filterCategory === cat ? 'rgba(0, 119, 133, 0.1)' : 'transparent',
                  color: filterCategory === cat ? '#007785' : '#888888'
                }}
              >
                {cat === 'all' ? 'All' : `Grade ${cat}`}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Candidates Table */}
      <div 
        className="backdrop-blur-xl rounded-2xl border shadow-xl overflow-hidden"
        style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
      >
        <table className="w-full">
          <thead>
            <tr style={{ backgroundColor: 'rgba(0, 119, 133, 0.05)' }}>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('name')}
                  className="flex items-center space-x-2 text-sm font-bold uppercase tracking-wider"
                  style={{ color: '#313335' }}
                >
                  <span>Candidate</span>
                  <ArrowUpDown className="w-4 h-4" strokeWidth={2} />
                </button>
              </th>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('score')}
                  className="flex items-center space-x-2 text-sm font-bold uppercase tracking-wider"
                  style={{ color: '#313335' }}
                >
                  <span>Score</span>
                  <ArrowUpDown className="w-4 h-4" strokeWidth={2} />
                </button>
              </th>
              <th className="px-6 py-4 text-left">
                <span className="text-sm font-bold uppercase tracking-wider" style={{ color: '#313335' }}>
                  Grade
                </span>
              </th>
              <th className="px-6 py-4 text-left">
                <span className="text-sm font-bold uppercase tracking-wider" style={{ color: '#313335' }}>
                  Status
                </span>
              </th>
              <th className="px-6 py-4 text-left">
                <button
                  onClick={() => handleSort('date')}
                  className="flex items-center space-x-2 text-sm font-bold uppercase tracking-wider"
                  style={{ color: '#313335' }}
                >
                  <span>Applied</span>
                  <ArrowUpDown className="w-4 h-4" strokeWidth={2} />
                </button>
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center">
                  <Users className="w-16 h-16 mx-auto mb-4" style={{ color: '#CACCCE' }} />
                  <p className="text-lg font-semibold" style={{ color: '#888888' }}>
                    {searchTerm || filterCategory !== 'all' ? 'No candidates match your filters' : 'No candidates yet'}
                  </p>
                </td>
              </tr>
            ) : (
              filteredCandidates.map((candidate: any) => {
                const category = getCategory(candidate.cv_score || 0)
                const categoryColor = getCategoryColor(category)

                return (
                  <tr 
                    key={candidate.id}
                    className="border-t hover:bg-white/50 transition-all"
                    style={{ borderColor: 'rgba(202, 204, 206, 0.2)' }}
                  >
                    <td className="px-6 py-4">
                      <Link 
                        to={`/candidates/${candidate.id}`}
                        className="flex items-center space-x-3 hover:opacity-80"
                      >
                        <div 
                          className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-lg"
                          style={{ background: `linear-gradient(135deg, ${categoryColor} 0%, #007785 100%)` }}
                        >
                          {(candidate.first_name || 'U')[0]}{(candidate.last_name || '')[0]}
                        </div>
                        <div>
                          <p className="font-semibold" style={{ color: '#313335' }}>
                            {candidate.first_name} {candidate.last_name}
                          </p>
                          <p className="text-sm" style={{ color: '#888888' }}>{candidate.email}</p>
                        </div>
                      </Link>
                    </td>

                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <span className="text-xl font-bold" style={{ color: categoryColor }}>
                          {(candidate.cv_score || 0).toFixed(1)}
                        </span>
                        <div className="flex-1 min-w-[80px]">
                          <div className="h-2 rounded-full" style={{ backgroundColor: 'rgba(202, 204, 206, 0.3)' }}>
                            <div 
                              className="h-full rounded-full transition-all"
                              style={{ 
                                width: `${candidate.cv_score || 0}%`,
                                backgroundColor: categoryColor
                              }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span 
                        className="px-3 py-1.5 rounded-xl text-sm font-bold"
                        style={{ 
                          backgroundColor: `${categoryColor}15`,
                          color: categoryColor
                        }}
                      >
                        {category}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <span 
                        className="px-3 py-1.5 rounded-xl text-sm font-bold capitalize"
                        style={{ 
                          backgroundColor: candidate.application_status === 'accepted' ? 'rgba(0, 119, 133, 0.1)' :
                                          candidate.application_status === 'rejected' ? 'rgba(221, 81, 67, 0.1)' :
                                          'rgba(230, 133, 35, 0.1)',
                          color: candidate.application_status === 'accepted' ? '#007785' :
                                candidate.application_status === 'rejected' ? '#DD5143' : '#E68523'
                        }}
                      >
                        {candidate.application_status || 'pending'}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <span className="text-sm font-medium" style={{ color: '#888888' }}>
                        {new Date(candidate.applied_at || candidate.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric'
                        })}
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
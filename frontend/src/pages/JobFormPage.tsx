import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import { jobsApi } from '../services/api'
import { ArrowLeft, Save, Sparkles } from 'lucide-react'

export default function JobFormPage() {
  const navigate = useNavigate()
  const { id } = useParams()
  const isEdit = !!id

  const [formData, setFormData] = useState({
    title: '',
    industry: '',
    location: '',
    contract_type: 'CDI',
    description: '',
    responsibilities: '',
    required_skills: [] as string[],
    nice_to_have_skills: [] as string[],
    experience_min_years: 0,
    experience_max_years: 0,
    experience_level: '',
    education_level: '',
    education_field: '',
    languages: [] as Array<{ name: string; level: string }>,
    salary_min: 0,
    salary_max: 0,
    benefits: '',
    is_active: true,
  })

  const [skillInput, setSkillInput] = useState('')
  const [niceSkillInput, setNiceSkillInput] = useState('')
  const [languageName, setLanguageName] = useState('')
  const [languageLevel, setLanguageLevel] = useState('')

  // Charger le job si mode édition
  const { data: job } = useQuery({
    queryKey: ['job', id],
    queryFn: () => jobsApi.getById(Number(id)),
    enabled: isEdit,
  })

  useEffect(() => {
    if (job) {
      setFormData({
        ...job,
        required_skills: job.required_skills || [],
        nice_to_have_skills: job.nice_to_have_skills || [],
        languages: job.languages || [],
      })
    }
  }, [job])

  const mutation = useMutation({
    mutationFn: (data: any) => isEdit ? jobsApi.update(Number(id), data) : jobsApi.create(data),
    onSuccess: () => {
      navigate('/jobs')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  const addSkill = () => {
    if (skillInput.trim()) {
      setFormData({ ...formData, required_skills: [...formData.required_skills, skillInput.trim()] })
      setSkillInput('')
    }
  }

  const removeSkill = (index: number) => {
    setFormData({ ...formData, required_skills: formData.required_skills.filter((_, i) => i !== index) })
  }

  const addNiceSkill = () => {
    if (niceSkillInput.trim()) {
      setFormData({ ...formData, nice_to_have_skills: [...formData.nice_to_have_skills, niceSkillInput.trim()] })
      setNiceSkillInput('')
    }
  }

  const removeNiceSkill = (index: number) => {
    setFormData({ ...formData, nice_to_have_skills: formData.nice_to_have_skills.filter((_, i) => i !== index) })
  }

  const addLanguage = () => {
    if (languageName.trim() && languageLevel.trim()) {
      setFormData({ ...formData, languages: [...formData.languages, { name: languageName.trim(), level: languageLevel.trim() }] })
      setLanguageName('')
      setLanguageLevel('')
    }
  }

  const removeLanguage = (index: number) => {
    setFormData({ ...formData, languages: formData.languages.filter((_, i) => i !== index) })
  }

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
        
        <div className="relative flex items-center justify-between">
          <div className="flex items-center space-x-5">
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
            <div className="w-16 h-16 rounded-2xl backdrop-blur-xl flex items-center justify-center border"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                borderColor: 'rgba(255, 255, 255, 0.2)'
              }}
            >
              <Sparkles className="w-8 h-8 text-white" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">{isEdit ? 'Edit Job' : 'Create New Job'}</h1>
              <p className="text-white/80 text-base">Fill in the details to {isEdit ? 'update' : 'create'} a job offer</p>
            </div>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <h2 className="text-xl font-bold mb-6" style={{ color: '#313335' }}>Basic Information</h2>
          
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Job Title *</label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                placeholder="e.g., Senior Python Developer"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Industry *</label>
              <input
                type="text"
                required
                value={formData.industry}
                onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                placeholder="e.g., Technology"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Location *</label>
              <input
                type="text"
                required
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                placeholder="e.g., Paris, France"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Contract Type *</label>
              <select
                required
                value={formData.contract_type}
                onChange={(e) => setFormData({ ...formData, contract_type: e.target.value })}
                className="w-full px-4 py-3 rounded-xl border"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
              >
                <option value="CDI">CDI</option>
                <option value="CDD">CDD</option>
                <option value="Freelance">Freelance</option>
                <option value="Stage">Stage</option>
              </select>
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Description *</label>
            <textarea
              required
              rows={4}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border resize-none"
              style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
              placeholder="Job description..."
            />
          </div>

          <div className="mt-6">
            <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Responsibilities *</label>
            <textarea
              required
              rows={3}
              value={formData.responsibilities}
              onChange={(e) => setFormData({ ...formData, responsibilities: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border resize-none"
              style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
              placeholder="Separate with periods. E.g., Develop APIs. Optimize performance."
            />
          </div>
        </div>

        {/* Skills Section */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <h2 className="text-xl font-bold mb-6" style={{ color: '#313335' }}>Skills & Requirements</h2>
          
          <div className="space-y-6">
            {/* Required Skills */}
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Required Skills</label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  className="flex-1 px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                  placeholder="Add a skill..."
                />
                <button
                  type="button"
                  onClick={addSkill}
                  className="px-6 py-3 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105"
                  style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.required_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 rounded-xl text-sm font-semibold flex items-center gap-2"
                    style={{ backgroundColor: 'rgba(0, 119, 133, 0.1)', color: '#007785' }}
                  >
                    {skill}
                    <button type="button" onClick={() => removeSkill(idx)} className="hover:scale-125">×</button>
                  </span>
                ))}
              </div>
            </div>

            {/* Nice to Have Skills */}
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Nice to Have Skills</label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={niceSkillInput}
                  onChange={(e) => setNiceSkillInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addNiceSkill())}
                  className="flex-1 px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                  placeholder="Add a skill..."
                />
                <button
                  type="button"
                  onClick={addNiceSkill}
                  className="px-6 py-3 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105"
                  style={{ background: 'linear-gradient(135deg, #00ACDC 0%, #8D6CAB 100%)' }}
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.nice_to_have_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 rounded-xl text-sm font-semibold flex items-center gap-2"
                    style={{ backgroundColor: 'rgba(141, 108, 171, 0.1)', color: '#8D6CAB' }}
                  >
                    {skill}
                    <button type="button" onClick={() => removeNiceSkill(idx)} className="hover:scale-125">×</button>
                  </span>
                ))}
              </div>
            </div>

            {/* Languages */}
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Languages</label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={languageName}
                  onChange={(e) => setLanguageName(e.target.value)}
                  className="flex-1 px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                  placeholder="Language name..."
                />
                <input
                  type="text"
                  value={languageLevel}
                  onChange={(e) => setLanguageLevel(e.target.value)}
                  className="flex-1 px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                  placeholder="Level (e.g., Natif, Courant)..."
                />
                <button
                  type="button"
                  onClick={addLanguage}
                  className="px-6 py-3 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105"
                  style={{ background: 'linear-gradient(135deg, #E68523 0%, #DD5143 100%)' }}
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.languages.map((lang, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 rounded-xl text-sm font-semibold flex items-center gap-2"
                    style={{ backgroundColor: 'rgba(230, 133, 35, 0.1)', color: '#E68523' }}
                  >
                    {lang.name} - {lang.level}
                    <button type="button" onClick={() => removeLanguage(idx)} className="hover:scale-125">×</button>
                  </span>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Experience Level</label>
                <select
                  value={formData.experience_level}
                  onChange={(e) => setFormData({ ...formData, experience_level: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                >
                  <option value="">Select...</option>
                  <option value="Junior">Junior</option>
                  <option value="Confirmé">Confirmé</option>
                  <option value="Senior">Senior</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Min Years</label>
                <input
                  type="number"
                  value={formData.experience_min_years}
                  onChange={(e) => setFormData({ ...formData, experience_min_years: Number(e.target.value) })}
                  className="w-full px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Max Years</label>
                <input
                  type="number"
                  value={formData.experience_max_years}
                  onChange={(e) => setFormData({ ...formData, experience_max_years: Number(e.target.value) })}
                  className="w-full px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Education Level</label>
                <input
                  type="text"
                  value={formData.education_level}
                  onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                  placeholder="e.g., Bac+5"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Education Field</label>
                <input
                  type="text"
                  value={formData.education_field}
                  onChange={(e) => setFormData({ ...formData, education_field: e.target.value })}
                  className="w-full px-4 py-3 rounded-xl border"
                  style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
                  placeholder="e.g., Informatique"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Salary & Benefits */}
        <div 
          className="backdrop-blur-xl rounded-2xl p-6 border shadow-xl"
          style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', borderColor: 'rgba(202, 204, 206, 0.3)' }}
        >
          <h2 className="text-xl font-bold mb-6" style={{ color: '#313335' }}>Compensation & Benefits</h2>
          
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Min Salary (€)</label>
              <input
                type="number"
                value={formData.salary_min}
                onChange={(e) => setFormData({ ...formData, salary_min: Number(e.target.value) })}
                className="w-full px-4 py-3 rounded-xl border"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Max Salary (€)</label>
              <input
                type="number"
                value={formData.salary_max}
                onChange={(e) => setFormData({ ...formData, salary_max: Number(e.target.value) })}
                className="w-full px-4 py-3 rounded-xl border"
                style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
              />
            </div>
          </div>

          <div className="mt-6">
            <label className="block text-sm font-semibold mb-2" style={{ color: '#313335' }}>Benefits</label>
            <textarea
              rows={3}
              value={formData.benefits}
              onChange={(e) => setFormData({ ...formData, benefits: e.target.value })}
              className="w-full px-4 py-3 rounded-xl border resize-none"
              style={{ backgroundColor: 'rgba(243, 242, 239, 0.5)', borderColor: 'rgba(202, 204, 206, 0.3)', color: '#313335' }}
              placeholder="Separate with periods. E.g., Télétravail. Tickets restaurant. Mutuelle."
            />
          </div>

          <div className="mt-6 flex items-center space-x-3">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-5 h-5 rounded"
            />
            <label htmlFor="is_active" className="text-sm font-semibold" style={{ color: '#313335' }}>
              Active (visible to candidates)
            </label>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/jobs')}
            className="px-8 py-4 rounded-xl font-semibold transition-all hover:scale-105"
            style={{ backgroundColor: 'rgba(136, 136, 136, 0.1)', color: '#888888' }}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="px-8 py-4 rounded-xl font-semibold text-white shadow-xl transition-all hover:scale-105 flex items-center gap-2"
            style={{ background: 'linear-gradient(135deg, #007785 0%, #00ACDC 100%)' }}
          >
            <Save className="w-5 h-5" strokeWidth={2.5} />
            {mutation.isPending ? 'Saving...' : isEdit ? 'Update Job' : 'Create Job'}
          </button>
        </div>
      </form>
    </div>
  )
}
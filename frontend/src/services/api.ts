import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || (window.location.hostname.includes('onrender.com')
  ? `https://${window.location.hostname}/api`
  : 'http://localhost:8001/api')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ========== JOBS API ==========

export const jobsApi = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/jobs/?skip=${skip}&limit=${limit}`)
    return response.data
  },

  getById: async (id: number) => {
    const response = await api.get(`/jobs/${id}`)
    return response.data
  },

  create: async (data: any) => {
    const response = await api.post('/jobs/create', data)
    return response.data
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/jobs/${id}`, data)
    return response.data
  },

  delete: async (id: number) => {
    const response = await api.delete(`/jobs/${id}`)
    return response.data
  },

  generateLinkedIn: async (jobId: number) => {
    const response = await api.post('/jobs/generate-linkedin', {
      job_offer_id: jobId
    })
    return response.data
  },

  getLinkedInPost: async (id: number) => {
    const response = await api.get(`/jobs/${id}/linkedin-post`)
    return response.data
  },

  // Publication automatique LinkedIn
  publishToLinkedIn: async (jobId: number, regenerate: boolean = false) => {
    const response = await api.post(`/jobs/${jobId}/publish-linkedin`, { regenerate })
    return response.data
  },
}

// ========== CANDIDATES API ==========

export const candidatesApi = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get(`/candidates/?skip=${skip}&limit=${limit}`)
    return response.data
  },

  getById: async (id: number) => {
    const response = await api.get(`/candidates/${id}`)
    return response.data
  },

  uploadCV: async (file: File, jobOfferId: number) => {
    const formData = new FormData()
    formData.append('cv_file', file)  // ✅ CHANGÉ : 'cv_file' au lieu de 'file'

    // ✅ CHANGÉ : job_offer_id en query parameter
    const response = await api.post(
      `/candidates/upload-cv?job_offer_id=${jobOfferId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  getAnalysis: async (id: number) => {
    const response = await api.get(`/candidates/${id}/analysis`)
    return response.data
  },

  getByJob: async (jobId: number) => {
    const response = await api.get(`/candidates/by-job/${jobId}`)
    return response.data
  },

  getRanking: async (jobId: number) => {
    const response = await api.get(`/candidates/ranking/${jobId}`)
    return response.data
  },

  downloadCV: async (id: number) => {
    const response = await api.get(`/candidates/${id}/download-cv`, {
      responseType: 'blob',
    })
    return response.data
  },

  exportExcel: async (jobId?: number) => {
    const url = jobId ? `/candidates/export/excel?job_id=${jobId}` : '/candidates/export/excel'
    const response = await api.get(url, {
      responseType: 'blob',
    })
    return response.data
  },

  update: async (id: number, data: any) => {
    const response = await api.put(`/candidates/${id}`, data)
    return response.data
  },

  delete: async (id: number) => {
    const response = await api.delete(`/candidates/${id}`)
    return response.data
  },
  getImprovedAnalysis: (id: number) => 
    api.get(`/candidates/${id}/analysis-improved`).then(res => res.data),
}

// ========== STATS API ==========

export const statsApi = {
  getGlobalStats: async () => {
    const response = await api.get('/candidates/stats/global')
    return response.data
  },

  getJobStats: async (jobId: number) => {
    const response = await api.get(`/candidates/stats/by-job/${jobId}`)
    return response.data
  },
}

// ========== INTERVIEWS API ==========

export const interviewApi = {
  // Démarrer un entretien
  start: async (candidateId: number, jobOfferId: number) => {
    const response = await api.post('/interviews/start', {
      candidate_id: candidateId,
      job_offer_id: jobOfferId
    })
    return response.data
  },

  // Envoyer une réponse
  respond: async (sessionId: string, questionId: string, responseText: string) => {
    const response = await api.post(`/interviews/${sessionId}/respond`, {
      question_id: questionId,
      response_text: responseText,
      response_time: Math.floor(Math.random() * 60) + 30
    })
    return response.data
  },

  // Obtenir le score
  getScore: async (sessionId: string) => {
    const response = await api.get(`/interviews/${sessionId}/score`)
    return response.data
  },

  // Obtenir l'historique
  getHistory: async (sessionId: string) => {
    const response = await api.get(`/interviews/${sessionId}/history`)
    return response.data
  }


  
}


// ============ LINKEDIN API ============
export const linkedinApi = {
  // Obtenir l'URL de connexion
  getConnectUrl: async () => {
    const response = await api.get(`/linkedin/connect`)
    return response.data
  },

  // Vérifier le statut
  getStatus: async () => {
    const response = await api.get(`/linkedin/status`)
    return response.data
  },

  // Publier un post
  publish: async (text: string, visibility: string = 'PUBLIC') => {
    const response = await api.post(`/linkedin/publish`, { text, visibility })
    return response.data
  },

  // Déconnecter
  disconnect: async () => {
    const response = await api.delete(`/linkedin/disconnect`)
    return response.data
  }
}

export default api
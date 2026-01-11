// Types pour les offres d'emploi
export interface JobOffer {
  id: number;
  title: string;
  department: string;
  location: string;
  contract_type: string;
  experience_required: string;
  salary_range?: string;
  skills_required: string[];
  description?: string;
  responsibilities?: string[];
  profile_sought?: string[];
  benefits?: string[];
  linkedin_post?: string;
  created_at: string;
  updated_at: string;
  status: 'draft' | 'published' | 'closed';
}

// Types pour les candidats
export interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  cv_file_path: string;
  job_offer_id: number;
  cv_score: number;
  final_score?: number;
  application_status: 'pending' | 'reviewing' | 'interviewed' | 'accepted' | 'rejected';
  applied_at: string;
  extracted_data?: ExtractedData;
  score_breakdown?: ScoreBreakdown;
}

// Données extraites du CV
export interface ExtractedData {
  contact: {
    name?: string;
    email?: string;
    phone?: string;
  };
  skills: string[];
  experience_years?: number;
  education: Education[];
  languages: Language[];
  extraction_method?: string;
}

export interface Education {
  degree: string;
  field?: string;
  year?: string;
}

export interface Language {
  language: string;
  level: string;
}

// Score détaillé
export interface ScoreBreakdown {
  skills: number;
  experience: number;
  education: number;
  languages: number;
}

// Analyse complète d'un candidat
export interface CandidateAnalysis {
  candidate: Candidate;
  matching_details: MatchingDetails;
  recommendation: string;
  category: string;
}

export interface MatchingDetails {
  matched_skills: string[];
  missing_skills: string[];
  match_score: number;
  experience_score: number;
  education_score: number;
  languages_score: number;
}

// Statistiques
export interface JobStatistics {
  job_id: number;
  job_title: string;
  total_candidates: number;
  scores: {
    average: number;
    min: number;
    max: number;
    median: number;
  };
  categories: {
    A: number;
    B: number;
    C: number;
    D: number;
  };
  top_skills: Array<{
    skill: string;
    count: number;
    percentage: number;
  }>;
}

export interface GlobalStatistics {
  total_jobs: number;
  total_candidates: number;
  average_score: number;
  quality_distribution: {
    excellent: number;
    good: number;
    average: number;
    poor: number;
  };
}

// Réponses API
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Formulaires
export interface CreateJobForm {
  title: string;
  department: string;
  location: string;
  contract_type: string;
  experience_required: string;
  salary_range?: string;
  skills_required: string[];
  description?: string;
}

export interface GenerateLinkedInForm {
  job_id: number;
  template?: string;
  tone?: string;
}
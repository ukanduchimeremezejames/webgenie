/**
 * API Client Service
 * Handles all REST API calls to the WebGenie backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ==================== DATASET ENDPOINTS ====================

export interface Dataset {
  id: string;
  name: string;
  description: string;
  source: string;
  species?: string;
  tissue?: string;
  genes?: number;
  samples?: number;
  created_at: string;
  updated_at: string;
}

export interface DatasetCreate {
  name: string;
  description: string;
  source: string;
  schema?: Record<string, unknown>;
  species?: string;
  tissue?: string;
}

export const datasetApi = {
  /**
   * List all datasets with pagination
   */
  list: async (skip: number = 0, limit: number = 10): Promise<PaginatedResponse<Dataset>> => {
    const response = await fetch(
      `${API_BASE_URL}/datasets?skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }
    );
    if (!response.ok) throw new Error('Failed to fetch datasets');
    return response.json();
  },

  /**
   * Get a specific dataset by ID
   */
  get: async (datasetId: string): Promise<Dataset> => {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch dataset');
    return response.json();
  },

  /**
   * Get dataset preview
   */
  getPreview: async (datasetId: string, numRows: number = 5): Promise<Record<string, unknown>> => {
    const response = await fetch(
      `${API_BASE_URL}/datasets/${datasetId}/preview?num_rows=${numRows}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }
    );
    if (!response.ok) throw new Error('Failed to fetch dataset preview');
    return response.json();
  },

  /**
   * Register a new dataset
   */
  register: async (dataset: DatasetCreate): Promise<Dataset> => {
    const response = await fetch(`${API_BASE_URL}/datasets/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dataset),
    });
    if (!response.ok) throw new Error('Failed to register dataset');
    return response.json();
  },

  /**
   * Update dataset metadata
   */
  update: async (datasetId: string, updates: Partial<Dataset>): Promise<Dataset> => {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update dataset');
    return response.json();
  },

  /**
   * Delete a dataset
   */
  delete: async (datasetId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/datasets/${datasetId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete dataset');
  },
};

// ==================== ALGORITHM ENDPOINTS ====================

export interface Algorithm {
  name: string;
  description: string;
  docker_image: string;
  parameters: Record<string, unknown>;
  version: string;
  authors?: string[];
  citation?: string;
}

export interface AlgorithmListResponse {
  algorithms: Algorithm[];
  total: number;
  registry: string;
}

export const algorithmApi = {
  /**
   * List all available algorithms from Docker Hub
   */
  list: async (): Promise<AlgorithmListResponse> => {
    const response = await fetch(`${API_BASE_URL}/algorithms`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch algorithms');
    return response.json();
  },

  /**
   * Get a specific algorithm details
   */
  get: async (algorithmName: string): Promise<Algorithm> => {
    const response = await fetch(`${API_BASE_URL}/algorithms/${algorithmName}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch algorithm');
    return response.json();
  },
};

// ==================== JOB ENDPOINTS ====================

export enum JobStatus {
  PENDING = 'PENDING',
  RUNNING = 'RUNNING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
}

export interface Job {
  id: string;
  name: string;
  description?: string;
  dataset_id: string;
  algorithm: string;
  status: JobStatus;
  parameters: Record<string, unknown>;
  progress?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface JobCreate {
  name: string;
  description?: string;
  dataset_id: string;
  algorithm: string;
  parameters?: Record<string, unknown>;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  skip: number;
  limit: number;
}

export const jobApi = {
  /**
   * List all jobs with optional filters
   */
  list: async (
    skip: number = 0,
    limit: number = 10,
    status?: JobStatus,
    datasetId?: string,
    algorithm?: string
  ): Promise<JobListResponse> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (status) params.append('status', status);
    if (datasetId) params.append('dataset_id', datasetId);
    if (algorithm) params.append('algorithm', algorithm);

    const response = await fetch(`${API_BASE_URL}/jobs?${params}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch jobs');
    return response.json();
  },

  /**
   * Get a specific job by ID
   */
  get: async (jobId: string): Promise<Job> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch job');
    return response.json();
  },

  /**
   * Submit a new job
   */
  submit: async (job: JobCreate): Promise<Job> => {
    const response = await fetch(`${API_BASE_URL}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(job),
    });
    if (!response.ok) throw new Error('Failed to submit job');
    return response.json();
  },

  /**
   * Get job logs
   */
  getLogs: async (jobId: string): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/logs`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch job logs');
    const data = await response.json();
    return data.logs || '';
  },

  /**
   * Cancel a job
   */
  cancel: async (jobId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to cancel job');
  },
};

// ==================== RESULT ENDPOINTS ====================

export interface Result {
  id: string;
  job_id: string;
  network_file?: string;
  metrics?: Record<string, unknown>;
  created_at: string;
  format?: string;
}

export interface ResultListResponse {
  items: Result[];
  total: number;
  skip: number;
  limit: number;
}

export const resultApi = {
  /**
   * List results with optional filters
   */
  list: async (
    skip: number = 0,
    limit: number = 10,
    jobId?: string
  ): Promise<ResultListResponse> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (jobId) params.append('job_id', jobId);

    const response = await fetch(`${API_BASE_URL}/results?${params}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch results');
    return response.json();
  },

  /**
   * Get a specific result by ID
   */
  get: async (resultId: string): Promise<Result> => {
    const response = await fetch(`${API_BASE_URL}/results/${resultId}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to fetch result');
    return response.json();
  },

  /**
   * Download result file
   */
  download: async (resultId: string, format: string = 'graphml'): Promise<Blob> => {
    const response = await fetch(
      `${API_BASE_URL}/results/${resultId}/download?format=${format}`,
      {
        method: 'GET',
      }
    );
    if (!response.ok) throw new Error('Failed to download result');
    return response.blob();
  },

  /**
   * Delete a result
   */
  delete: async (resultId: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/results/${resultId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete result');
  },
};

// ==================== HEALTH & STATUS ENDPOINTS ====================

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  uptime: number;
  database: boolean;
  redis: boolean;
  celery_worker: boolean;
}

export const healthApi = {
  /**
   * Check backend health status
   */
  check: async (): Promise<HealthStatus> => {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
      method: 'GET',
    });
    if (!response.ok) throw new Error('Failed to check health');
    return response.json();
  },
};

// ==================== ERROR HANDLING ====================

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Global error handler for API calls
 */
export const handleApiError = (error: unknown): ApiError => {
  if (error instanceof ApiError) {
    return error;
  }
  if (error instanceof Error) {
    return new ApiError(500, error.message);
  }
  return new ApiError(500, 'An unexpected error occurred');
};

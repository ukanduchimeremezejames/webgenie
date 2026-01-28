/**
 * React hooks for API calls
 * Simplifies data fetching and state management
 */

import { useState, useEffect, useCallback } from 'react';
import * as api from './api';

// ==================== GENERIC HOOKS ====================

interface UseAsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  immediate = true
): UseAsyncState<T> & { execute: () => Promise<void> } {
  const [state, setState] = useState<UseAsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await asyncFunction();
      setState({ data: result, loading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        loading: false,
        error: error instanceof Error ? error : new Error('Unknown error'),
      });
    }
  }, [asyncFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { ...state, execute };
}

// ==================== DATASET HOOKS ====================

export function useDatasets(skip: number = 0, limit: number = 10) {
  return useAsync(
    () => api.datasetApi.list(skip, limit),
    true
  );
}

export function useDataset(datasetId: string | null) {
  return useAsync(
    () => (datasetId ? api.datasetApi.get(datasetId) : Promise.reject('No dataset ID')),
    !!datasetId
  );
}

export function useDatasetPreview(datasetId: string | null, numRows: number = 5) {
  return useAsync(
    () => (datasetId ? api.datasetApi.getPreview(datasetId, numRows) : Promise.reject('No dataset ID')),
    !!datasetId
  );
}

// ==================== ALGORITHM HOOKS ====================

export function useAlgorithms() {
  return useAsync(() => api.algorithmApi.list(), true);
}

export function useAlgorithm(algorithmName: string | null) {
  return useAsync(
    () => (algorithmName ? api.algorithmApi.get(algorithmName) : Promise.reject('No algorithm name')),
    !!algorithmName
  );
}

// ==================== JOB HOOKS ====================

export function useJobs(
  skip: number = 0,
  limit: number = 10,
  status?: api.JobStatus,
  datasetId?: string,
  algorithm?: string
) {
  return useAsync(
    () => api.jobApi.list(skip, limit, status, datasetId, algorithm),
    true
  );
}

export function useJob(jobId: string | null) {
  return useAsync(
    () => (jobId ? api.jobApi.get(jobId) : Promise.reject('No job ID')),
    !!jobId
  );
}

export function useJobLogs(jobId: string | null) {
  return useAsync(
    () => (jobId ? api.jobApi.getLogs(jobId) : Promise.reject('No job ID')),
    !!jobId
  );
}

export function useSubmitJob() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const submit = useCallback(async (job: api.JobCreate) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.jobApi.submit(job);
      setLoading(false);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      setLoading(false);
      throw error;
    }
  }, []);

  return { submit, loading, error };
}

export function useCancelJob() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const cancel = useCallback(async (jobId: string) => {
    setLoading(true);
    setError(null);
    try {
      await api.jobApi.cancel(jobId);
      setLoading(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      setLoading(false);
      throw error;
    }
  }, []);

  return { cancel, loading, error };
}

// ==================== RESULT HOOKS ====================

export function useResults(
  skip: number = 0,
  limit: number = 10,
  jobId?: string
) {
  return useAsync(
    () => api.resultApi.list(skip, limit, jobId),
    true
  );
}

export function useResult(resultId: string | null) {
  return useAsync(
    () => (resultId ? api.resultApi.get(resultId) : Promise.reject('No result ID')),
    !!resultId
  );
}

export function useDownloadResult() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const download = useCallback(async (resultId: string, format: string = 'graphml') => {
    setLoading(true);
    setError(null);
    try {
      const blob = await api.resultApi.download(resultId, format);
      
      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `result-${resultId}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      setLoading(false);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      setLoading(false);
      throw error;
    }
  }, []);

  return { download, loading, error };
}

// ==================== HEALTH HOOK ====================

export function useHealth() {
  return useAsync(() => api.healthApi.check(), true);
}

// ==================== POLLING HOOK ====================

interface UsePollOptions {
  interval?: number;
  enabled?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function usePoll<T>(
  asyncFunction: () => Promise<T>,
  options: UsePollOptions = {}
) {
  const { interval = 5000, enabled = true, onSuccess, onError } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!enabled) return;

    let timeoutId: NodeJS.Timeout;

    const poll = async () => {
      try {
        setLoading(true);
        const result = await asyncFunction();
        setData(result);
        setError(null);
        onSuccess?.(result);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Unknown error');
        setError(error);
        onError?.(error);
      } finally {
        setLoading(false);
        timeoutId = setTimeout(poll, interval);
      }
    };

    poll();

    return () => clearTimeout(timeoutId);
  }, [asyncFunction, interval, enabled, onSuccess, onError]);

  return { data, loading, error };
}

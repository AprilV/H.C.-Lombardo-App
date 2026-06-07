const API_URL = process.env.REACT_APP_API_URL ?? '';

const normalizeSeason = (season) => {
  const parsed = Number.parseInt(season, 10);
  if (!Number.isFinite(parsed)) {
    throw new Error('A valid season is required for ML API requests.');
  }
  return parsed;
};

export const getPerformanceStatsUrl = (season, { week, lite } = {}) => {
  const safeSeason = normalizeSeason(season);
  const params = new URLSearchParams({ season: String(safeSeason) });

  if (week !== undefined && week !== null) {
    params.set('week', String(week));
  }

  if (lite) {
    params.set('lite', '1');
  }

  return `${API_URL}/api/ml/performance-stats?${params.toString()}`;
};

export const getSeasonAiVsVegasUrl = (season) => {
  const safeSeason = normalizeSeason(season);
  return `${API_URL}/api/ml/season-ai-vs-vegas/${safeSeason}`;
};

export const getAiVsVegasReconciliationUrl = (
  season,
  {
    strictMode,
    includePerformanceContract,
    sampleLimit
  } = {}
) => {
  const safeSeason = normalizeSeason(season);
  const params = new URLSearchParams({ season: String(safeSeason) });

  if (strictMode !== undefined) {
    params.set('strict_mode', strictMode ? 'true' : 'false');
  }

  if (includePerformanceContract !== undefined) {
    params.set(
      'include_performance_contract',
      includePerformanceContract ? 'true' : 'false'
    );
  }

  if (sampleLimit !== undefined && sampleLimit !== null) {
    params.set('sample_limit', String(sampleLimit));
  }

  return `${API_URL}/api/ml/ai-vs-vegas-reconciliation?${params.toString()}`;
};

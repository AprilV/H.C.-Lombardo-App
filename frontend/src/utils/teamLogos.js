const TEAM_LOGO_ALIASES = {
  WSH: 'was',
  WAS: 'was',
  LAR: 'lar',
  LA: 'lar',
  LAC: 'lac',
};

const VALID_TEAM_ABBREVIATIONS = new Set([
  'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
  'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
  'LAC', 'LAR', 'LV', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
  'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS',
]);

const INVALID_TEAM_ABBREVIATIONS = new Set([
  'UNDEFINED',
  'NULL',
  'NAN',
  'NONE',
  'N/A',
  'NA',
  'TBD',
  '-',
]);

const NFL_LEAGUE_LOGO_URL = 'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';

const normalizeTeamAbbreviation = (teamAbbr) => {
  if (!teamAbbr || typeof teamAbbr !== 'string') {
    return null;
  }

  const normalized = teamAbbr.trim().toUpperCase();
  if (!normalized || INVALID_TEAM_ABBREVIATIONS.has(normalized)) {
    return null;
  }

  const canonical = TEAM_LOGO_ALIASES[normalized]
    ? TEAM_LOGO_ALIASES[normalized].toUpperCase()
    : normalized;

  if (!VALID_TEAM_ABBREVIATIONS.has(canonical)) {
    return null;
  }

  return canonical.toLowerCase();
};

export const getEspnTeamLogoUrl = (teamAbbr) => {
  const normalizedAbbr = normalizeTeamAbbreviation(teamAbbr);
  if (!normalizedAbbr) {
    return NFL_LEAGUE_LOGO_URL;
  }

  return `https://a.espncdn.com/i/teamlogos/nfl/500/${normalizedAbbr}.png`;
};
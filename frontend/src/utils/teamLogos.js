const TEAM_LOGO_ALIASES = {
  WSH: 'was',
  WAS: 'was',
  LAR: 'lar',
  LA: 'lar',
  LAC: 'lac',
};

const NFL_LEAGUE_LOGO_URL = 'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';

const normalizeTeamAbbreviation = (teamAbbr) => {
  if (!teamAbbr || typeof teamAbbr !== 'string') {
    return null;
  }

  const normalized = teamAbbr.trim().toUpperCase();
  if (!normalized) {
    return null;
  }

  return TEAM_LOGO_ALIASES[normalized] || normalized.toLowerCase();
};

export const getEspnTeamLogoUrl = (teamAbbr) => {
  const normalizedAbbr = normalizeTeamAbbreviation(teamAbbr);
  if (!normalizedAbbr) {
    return NFL_LEAGUE_LOGO_URL;
  }

  return `https://a.espncdn.com/i/teamlogos/nfl/500/${normalizedAbbr}.png`;
};
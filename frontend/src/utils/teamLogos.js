const ESPN_LOGO_BASE_URL = 'https://a.espncdn.com/i/teamlogos/nfl/500';

// Returns the ESPN logo URL for a team abbreviation (e.g., KC, sf, NYJ).
export function getEspnTeamLogoUrl(teamAbbr) {
  if (!teamAbbr) {
    return '';
  }

  return `${ESPN_LOGO_BASE_URL}/${String(teamAbbr).trim().toLowerCase()}.png`;
}

export default getEspnTeamLogoUrl;

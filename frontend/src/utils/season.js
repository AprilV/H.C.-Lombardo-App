export const MIN_NFL_SEASON = 1999;

export function getDefaultSeason(now = new Date()) {
  const year = now.getFullYear();
  const month = now.getMonth();

  // Offseason schedule + opening lines are typically available by spring.
  // Default to the current season from May onward so upcoming-game views
  // surface the live season instead of stale prior-season data.
  return month >= 4 ? year : year - 1;
}

export function getRecentSeasons(
  count = 4,
  minSeason = MIN_NFL_SEASON,
  anchorSeason = getDefaultSeason()
) {
  const seasons = [];

  for (let season = anchorSeason; season >= minSeason && seasons.length < count; season -= 1) {
    seasons.push(season);
  }

  return seasons;
}

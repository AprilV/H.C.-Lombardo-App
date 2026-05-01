export const MIN_NFL_SEASON = 1999;

export function getDefaultSeason(now = new Date()) {
  const year = now.getFullYear();
  const month = now.getMonth();

  // NFL regular season starts in late summer; before then default to prior season.
  return month >= 7 ? year : year - 1;
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

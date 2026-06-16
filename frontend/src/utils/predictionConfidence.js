const toNumber = (value) => {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
};

const spreadSide = (lineForPick) => {
  const numeric = toNumber(lineForPick);
  if (numeric === null || numeric === 0) {
    return 0;
  }

  return numeric < 0 ? -1 : 1;
};

const normalizeLineForPick = ({ homeTeam, pickTeam, spread }) => {
  const numericSpread = toNumber(spread);
  if (!homeTeam || !pickTeam || numericSpread === null) {
    return null;
  }

  return pickTeam === homeTeam ? numericSpread : -numericSpread;
};

export function getSpreadConfidence({
  homeTeam,
  pickTeam,
  eloSpread,
  aiSpread,
  edgePoints,
  minEdgeForStrong = 3
}) {
  const pickEloLine = normalizeLineForPick({ homeTeam, pickTeam, spread: eloSpread });
  const pickAiLine = normalizeLineForPick({ homeTeam, pickTeam, spread: aiSpread });

  const eloSide = spreadSide(pickEloLine);
  const aiSide = spreadSide(pickAiLine);
  const spreadsSameSide = eloSide !== 0 && eloSide === aiSide;

  const normalizedEdge = toNumber(edgePoints);
  const meaningfulEdge = normalizedEdge !== null && normalizedEdge >= minEdgeForStrong;

  const confidenceStrong = spreadsSameSide && meaningfulEdge;
  return {
    confidenceStrong,
    confidenceLabel: confidenceStrong ? 'Strong play' : 'Lean',
    confidenceDetail: confidenceStrong ? 'Both systems agree' : 'Close call',
    confidenceTone: confidenceStrong ? 'strong' : 'lean',
    spreadsSameSide,
    meaningfulEdge,
    pickEloLine,
    pickAiLine
  };
}

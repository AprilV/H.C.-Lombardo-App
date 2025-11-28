-- Add closing_spread column to store the final Vegas spread before kickoff
-- This locks in the "closing line" so we have consistent spread values for analysis

ALTER TABLE hcl.games 
ADD COLUMN IF NOT EXISTS closing_spread DOUBLE PRECISION;

COMMENT ON COLUMN hcl.games.closing_spread IS 'Final locked spread before kickoff (negative = home favored). This is the spread used for all betting analysis.';

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_games_closing_spread ON hcl.games(closing_spread) WHERE closing_spread IS NOT NULL;

-- For existing games with scores but no closing_spread, copy from spread_line
UPDATE hcl.games 
SET closing_spread = spread_line 
WHERE home_score IS NOT NULL 
  AND closing_spread IS NULL 
  AND spread_line IS NOT NULL;

COMMENT ON TABLE hcl.games IS 'Game metadata, betting lines (including locked closing spread), weather, and context for all NFL games';

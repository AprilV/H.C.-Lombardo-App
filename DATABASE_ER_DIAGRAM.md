```mermaid
erDiagram
    teams {
        integer id PK
        text name
        text abbreviation
        integer wins
        integer losses
        integer ties
        real ppg
        real pa
        integer games_played
        jsonb stats
        timestamp last_updated
    }
    
    stats_metadata {
        varchar stat_key PK
        varchar stat_name
        varchar category
        varchar data_type
        text description
        varchar source
        timestamp last_updated
    }
    
    update_metadata {
        integer id PK
        timestamp last_update
    }
```

**HC Lombardo Database - ER Diagram**

**Tables:**
1. **teams** - Stores all 32 NFL teams with current season data
2. **stats_metadata** - Defines available statistics that can be tracked
3. **update_metadata** - Tracks when database was last updated

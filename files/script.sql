CREATE TABLE IF NOT EXISTS users (
   UserID text PRIMARY KEY,
   MessagesSent integer DEFAULT 0,
   Coins integer DEFAULT 0,
   CoinLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS speedrun (
   GameName text DEFAULT None,
   GameID text DEFAULT None,
   CategoryName text DEFAULT None,
   CategoryID text DEFAULT None,
   SubcategoryName1 text DEFAULT None,
   SubcategoryID1 text DEFAULT None,
   SubcategoryName2 text DEFAULT None,
   SubcategoryID2 text DEFAULT None,
   SubcategoryName3 text DEFAULT None,
   SubcategoryID3 text DEFAULT None,
   SubcategoryName4 text DEFAULT None,
   SubcategoryID4 text DEFAULT None
);
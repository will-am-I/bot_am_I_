CREATE TABLE IF NOT EXISTS users (
   UserID text PRIMARY KEY,
   MessagesSent integer DEFAULT 0,
   Coins integer DEFAULT 0,
   CoinLock text DEFAULT CURRENT_TIMESTAMP
);
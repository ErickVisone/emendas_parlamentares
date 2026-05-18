from load import load_supabase_from_parquet

load_supabase_from_parquet("deputy_history", "bronze", "replace")

from supabase import create_client # pip install supabase
import os
supabase = create_client(os.getenv("SUPABASE_URL"),os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


# infrastructure/supabase.py
from supabase import create_client, Client
from core.config import settings
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY) # Cliente de Supabase admin
supabase_auth: Client= create_client(settings.SUPABASE_URL,settings.ANON_KEY) # Cliente de Supabase para autenticación de usuarios (registro, login, etc)
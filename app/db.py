import os 
from dotenv import load_dotenv
from supabase import create_client 


load_dotenv()


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SECRET_KEY = os.environ["SUPABASE_SECRET_KEY"]


supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


if __name__ == "__main__":
    result = supabase.table("chunks").select("*").execute()
    print(result.data)
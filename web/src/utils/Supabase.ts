import { createClient, SupabaseClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

class Supabase {
  private client: SupabaseClient | null = null;

  public getClient() {
    if (!this.client) {
      this.client = createClient(supabaseUrl, supabaseAnonKey);
    }
    return this.client;
  }

  public async getBearerToken() {
    const session = await this.getClient()?.auth?.getSession();
    return session?.data?.session?.access_token;
  }
}

export default new Supabase();

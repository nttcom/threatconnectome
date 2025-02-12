import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

class Supabase {
  constructor() {
    this.client = null;
  }

  getClient() {
    if (!this.client) {
      this.client = createClient(supabaseUrl, supabaseAnonKey);
    }
    return this.client;
  }
}

export default new Supabase();

import type { AuthProvider } from "./AuthProvider";
import { FirebaseProvider } from "./FirebaseProvider";
import { SupabaseProvider } from "./SupabaseProvider";

export class AuthProviderFactory {
  static create(): AuthProvider {
    const provider = import.meta.env.VITE_AUTH_SERVICE;
    switch (provider) {
      case "supabase":
        return new SupabaseProvider();
      case "firebase":
        return new FirebaseProvider();
      default:
        throw new Error(`Unsupported VITE_AUTH_SERVICE: ${provider}`);
    }
  }
}

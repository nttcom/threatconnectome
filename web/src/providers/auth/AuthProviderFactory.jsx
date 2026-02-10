import { FirebaseProvider } from "./FirebaseProvider";
import { SupabaseProvider } from "./SupabaseProvider";
import i18n from "../../i18n/config";

export class AuthProviderFactory {
  static create() {
    const provider = import.meta.env.VITE_AUTH_SERVICE;
    switch (provider) {
      case "supabase":
        return new SupabaseProvider();
      case "firebase":
        return new FirebaseProvider();
      default:
        throw new Error(
          i18n.t("providers:AuthProviderFactory.unsupportedService", { service: provider }),
        );
    }
  }
}

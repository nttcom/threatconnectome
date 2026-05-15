import {
  applyActionCode,
  browserSessionPersistence,
  confirmPasswordReset,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  sendEmailVerification,
  sendPasswordResetEmail,
  setPersistence,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  verifyPasswordResetCode,
  multiFactor,
  RecaptchaVerifier,
  PhoneAuthProvider,
  PhoneMultiFactorGenerator,
  getMultiFactorResolver,
  type ActionCodeSettings,
  type Auth,
  type MultiFactorError,
  type MultiFactorResolver,
  type PhoneInfoOptions,
} from "firebase/auth";

import type {
  AuthStateCallbacks,
  EmailPasswordArgs,
  PhoneNumberExamples,
  RegisterPhoneNumberResult,
  SendEmailVerificationArgs,
  SendPasswordResetArgs,
  SignInResult,
  SignInWithEmailArgs,
  SmsLoginFlow,
} from "../../hooks/auth";
import i18n from "../../i18n/config";
import Firebase from "../../utils/Firebase";
import { getAuthErrorMessage } from "../../utils/authErrorUtils";
import { isE164Format } from "../../utils/phoneNumberUtils";

import { AuthData, AuthError, AuthProvider } from "./AuthProvider";

type ErrorLike = { code?: string; message?: string } | unknown;

function _errorToMessage(error: ErrorLike): string {
  const message = getAuthErrorMessage(error as never, {
    namespace: "providers",
    keyPrefix: "auth.FirebaseProvider",
    defaultMessage: i18n.t("auth.FirebaseProvider.internal-error", { ns: "providers" }),
  });
  return message;
}

class FirebaseAuthError extends AuthError {
  constructor(error: ErrorLike) {
    const code = (error as { code?: string })?.code;
    super(error, code, _errorToMessage(error));
    console.error("Authentication error:", this.message);
  }
}

async function startSmsLoginFlow(
  auth: Auth,
  error: MultiFactorError,
  recaptchaId: string,
): Promise<SmsLoginFlow | undefined> {
  const resolver: MultiFactorResolver = getMultiFactorResolver(auth, error);
  for (const hint of resolver.hints) {
    if (hint.factorId === PhoneMultiFactorGenerator.FACTOR_ID) {
      const phoneInfoOptions: PhoneInfoOptions = {
        multiFactorHint: hint,
        session: resolver.session,
      };

      const recaptchaVerifier = new RecaptchaVerifier(auth, recaptchaId, {
        size: "normal",
      });

      try {
        const phoneAuthProvider = new PhoneAuthProvider(auth);
        const verificationId = await phoneAuthProvider.verifyPhoneNumber(
          phoneInfoOptions,
          recaptchaVerifier,
        );
        return {
          mfa: true,
          resolver: resolver,
          verificationId: verificationId,
          phoneInfoOptions: phoneInfoOptions,
          auth: auth,
        };
      } catch (innerError) {
        recaptchaVerifier.clear();
        throw new FirebaseAuthError(innerError);
      }
    }
  }
  return undefined;
}

export class FirebaseProvider extends AuthProvider {
  override onAuthStateChanged({ signInCallback, signOutCallback }: AuthStateCallbacks): () => void {
    const unsubscribe = onAuthStateChanged(Firebase.getAuth(), (user) => {
      if (user) {
        signInCallback();
      } else {
        signOutCallback();
      }
    });
    return unsubscribe;
  }

  override async createUserWithEmailAndPassword({
    email,
    password,
  }: EmailPasswordArgs): Promise<AuthData> {
    return await createUserWithEmailAndPassword(Firebase.getAuth(), email, password)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async signInWithEmailAndPassword({
    email,
    password,
    recaptchaId,
  }: SignInWithEmailArgs): Promise<SignInResult> {
    const auth = Firebase.getAuth();
    return await setPersistence(auth, browserSessionPersistence)
      .then(() => signInWithEmailAndPassword(auth, email, password))
      .then((result) => {
        return new AuthData(result);
      })
      .catch(async (error: { code?: string }) => {
        if (error.code === "auth/multi-factor-auth-required") {
          if (!recaptchaId) {
            throw new FirebaseAuthError(error);
          }
          return await startSmsLoginFlow(auth, error as MultiFactorError, recaptchaId);
        } else {
          throw new FirebaseAuthError(error);
        }
      });
  }

  override async signInWithSamlPopup(): Promise<AuthData> {
    const samlProvider = Firebase.getSamlProvider();
    if (!samlProvider) {
      throw new FirebaseAuthError({
        code: "samlNotSupported",
        message: i18n.t("auth.FirebaseProvider.samlNotSupported", { ns: "providers" }),
      });
    }
    return await signInWithPopup(Firebase.getAuth(), samlProvider)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async signOut(): Promise<AuthData> {
    return await signOut(Firebase.getAuth())
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async sendEmailVerification({
    actionCodeSettings,
  }: SendEmailVerificationArgs): Promise<AuthData> {
    const currentUser = Firebase.getAuth().currentUser;
    if (!currentUser) {
      throw new FirebaseAuthError({ code: "auth/no-current-user" });
    }
    return await sendEmailVerification(currentUser, actionCodeSettings as ActionCodeSettings | null)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async sendPasswordResetEmail({
    email,
    actionCodeSettings,
  }: SendPasswordResetArgs): Promise<AuthData> {
    return await sendPasswordResetEmail(
      Firebase.getAuth(),
      email,
      actionCodeSettings as ActionCodeSettings | undefined,
    )
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async verifyPasswordResetCode({
    actionCode,
  }: {
    actionCode: string;
  }): Promise<AuthData> {
    return await verifyPasswordResetCode(Firebase.getAuth(), actionCode)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async confirmPasswordReset({
    actionCode,
    newPassword,
  }: {
    actionCode: string;
    newPassword: string;
  }): Promise<AuthData> {
    return await confirmPasswordReset(Firebase.getAuth(), actionCode, newPassword)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async applyActionCode({ actionCode }: { actionCode: string }): Promise<AuthData> {
    return await applyActionCode(Firebase.getAuth(), actionCode)
      .then((result) => {
        return new AuthData(result);
      })
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async registerPhoneNumber(
    phoneNumber: string,
    recaptchaId: string,
    phoneNumberExamples: PhoneNumberExamples = {},
  ): Promise<RegisterPhoneNumberResult> {
    if (!isE164Format(phoneNumber)) {
      throw new FirebaseAuthError({
        code: "auth/invalid-phone-number",
        message: i18n.t("auth.FirebaseProvider.invalidPhoneNumberExample", {
          ns: "providers",
          nationalExample: phoneNumberExamples.nationalExample,
          internationalExample: phoneNumberExamples.internationalExample,
        }),
      });
    }

    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;
    if (!currentUser) {
      throw new FirebaseAuthError({ code: "auth/no-current-user" });
    }

    const recaptchaVerifier = new RecaptchaVerifier(auth, recaptchaId, {
      size: "normal",
    });

    try {
      const multiFactorSession = await multiFactor(currentUser).getSession();
      const phoneInfoOptions: PhoneInfoOptions = {
        phoneNumber: phoneNumber,
        session: multiFactorSession,
      };
      const phoneAuthProvider = new PhoneAuthProvider(auth);
      const verificationId = await phoneAuthProvider.verifyPhoneNumber(
        phoneInfoOptions,
        recaptchaVerifier,
      ); // Send SMS verification code.
      return { verificationId: verificationId, phoneInfoOptions: phoneInfoOptions, auth: auth };
    } catch (error) {
      recaptchaVerifier.clear();
      throw new FirebaseAuthError(error);
    }
  }

  override async deletePhoneNumber(): Promise<void> {
    try {
      const auth = Firebase.getAuth();
      const currentUser = auth.currentUser;
      if (!currentUser) {
        throw new FirebaseAuthError({ code: "auth/no-current-user" });
      }
      const multiFactorUser = multiFactor(currentUser);
      for (const factor of multiFactorUser.enrolledFactors) {
        await multiFactorUser.unenroll(factor);
      }
    } catch (error) {
      throw new FirebaseAuthError(error);
    }
  }

  override async verifySmsForLogin(
    resolver: unknown,
    verificationId: string,
    verificationCode: string,
  ): Promise<unknown> {
    const cred = PhoneAuthProvider.credential(verificationId, verificationCode);
    const multiFactorAssertion = PhoneMultiFactorGenerator.assertion(cred);

    // Complete sign-in.
    return await (resolver as MultiFactorResolver)
      .resolveSignIn(multiFactorAssertion)
      .catch((error) => {
        throw new FirebaseAuthError(error);
      });
  }

  override async verifySmsForEnrollment(
    verificationId: string,
    verificationCode: string,
  ): Promise<void> {
    try {
      const auth = Firebase.getAuth();
      const currentUser = auth.currentUser;
      if (!currentUser) {
        throw new FirebaseAuthError({ code: "auth/no-current-user" });
      }
      const cred = PhoneAuthProvider.credential(verificationId, verificationCode);
      const multiFactorAssertion = PhoneMultiFactorGenerator.assertion(cred);

      // Complete enrollment.
      await multiFactor(currentUser).enroll(multiFactorAssertion, "My personal phone number");
    } catch (error) {
      throw new FirebaseAuthError(error);
    }
  }

  override async sendSmsCodeAgain(
    phoneInfoOptions: unknown,
    auth: unknown,
    recaptchaId: string,
  ): Promise<string> {
    const recaptchaForResend = Firebase.getRecaptchaForResend();

    if (recaptchaForResend) {
      recaptchaForResend.clear();
      Firebase.setRecaptchaForResend(null);
    }

    const typedAuth = auth as Auth;
    const recaptchaVerifier = new RecaptchaVerifier(typedAuth, recaptchaId, {
      size: "invisible",
    });
    Firebase.setRecaptchaForResend(recaptchaVerifier);

    const phoneAuthProvider = new PhoneAuthProvider(typedAuth);
    return await phoneAuthProvider
      .verifyPhoneNumber(phoneInfoOptions as PhoneInfoOptions, recaptchaVerifier)
      .then((verificationId) => {
        return verificationId;
      })
      .catch((error) => {
        recaptchaVerifier.clear();
        throw new FirebaseAuthError(error);
      });
  }

  override isSmsAuthenticationEnabled(): boolean {
    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;
    if (!currentUser) return false;
    const multiFactorUser = multiFactor(currentUser);
    for (const factor of multiFactorUser.enrolledFactors) {
      if (factor.factorId === "phone") {
        return true;
      }
    }
    return false;
  }

  override isAuthenticatedWithSaml(): boolean {
    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;
    if (!currentUser) return false;
    const isSamlUser = currentUser.providerData.some((provider) =>
      provider.providerId.startsWith("saml."),
    );
    return isSamlUser;
  }

  override getPhoneNumber(): string | null {
    const auth = Firebase.getAuth();
    const currentUser = auth.currentUser;
    if (!currentUser) return null;
    const multiFactorUser = multiFactor(currentUser);
    for (const factor of multiFactorUser.enrolledFactors) {
      if (factor.factorId === "phone") {
        // PhoneMultiFactorInfo has phoneNumber
        return (factor as { phoneNumber?: string }).phoneNumber ?? null;
      }
    }

    return null;
  }
}

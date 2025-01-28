import { createApi, fakeBaseQuery } from "@reduxjs/toolkit/query/react";
import {
  sendEmailVerification,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  createUserWithEmailAndPassword,
  applyActionCode,
  verifyPasswordResetCode,
  confirmPasswordReset,
} from "firebase/auth";

import { setAuthToken } from "../slices/auth";
import Firebase from "../utils/Firebase";

export const firebaseApi = createApi({
  reducerPath: "firebaseApi",
  baseQuery: fakeBaseQuery(),
  endpoints: (builder) => ({
    sendEmailVerification: builder.mutation({
      queryFn: async ({ user, actionCodeSettings }) => {
        return await sendEmailVerification(user, actionCodeSettings)
          .then((success) => {
            return { data: success };
          })
          .catch((error) => ({ error }));
      },
    }),
    sendPasswordResetEmail: builder.mutation({
      queryFn: async ({ email, actionCodeSettings }) => {
        return await sendPasswordResetEmail(Firebase.getAuth(), email, actionCodeSettings)
          .then((success) => {
            return { data: success };
          })
          .catch((error) => ({ error }));
      },
    }),
    signInWithEmailAndPassword: builder.mutation({
      queryFn: async ({ email, password }, { dispatch }) => {
        return await signInWithEmailAndPassword(Firebase.getAuth(), email, password)
          .then((credential) => {
            dispatch(setAuthToken(credential.user.accessToken));
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
    }),
    signInWithSamlPopup: builder.mutation({
      queryFn: async (_, { dispatch }) => {
        const samlProvider = Firebase.getSamlProvider();
        if (!samlProvider) {
          return { error: "SAML not supported" };
        }
        return await signInWithPopup(Firebase.getAuth(), samlProvider)
          .then((credential) => {
            dispatch(setAuthToken(credential.user.accessToken));
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
    }),
    createUserWithEmailAndPassword: builder.mutation({
      queryFn: async ({ email, password }) => {
        return await createUserWithEmailAndPassword(Firebase.getAuth(), email, password)
          .then((credential) => {
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
    }),
    applyActionCode: builder.mutation({
      queryFn: async ({ actionCode }) => {
        return await applyActionCode(Firebase.getAuth(), actionCode)
          .then(() => {
            return { data: { success: true, message: "Action code applied successfully" } };
          })
          .catch((error) => ({ error }));
      },
    }),
    verifyPasswordResetCode: builder.mutation({
      queryFn: async ({ actionCode }) => {
        return await verifyPasswordResetCode(Firebase.getAuth(), actionCode)
          .then((email) => {
            return {
              data: { success: true, email, message: "Password reset code verified successfully" },
            };
          })
          .catch((error) => ({ error }));
      },
    }),
    confirmPasswordReset: builder.mutation({
      queryFn: async ({ actionCode, newPassword }) => {
        return await confirmPasswordReset(Firebase.getAuth(), actionCode, newPassword)
          .then(() => {
            return { data: { success: true, message: "Password has been reset successfully" } };
          })
          .catch((error) => ({ error }));
      },
    }),
  }),
});

export const {
  useSendEmailVerificationMutation,
  useSendPasswordResetEmailMutation,
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
  useCreateUserWithEmailAndPasswordMutation,
  useApplyActionCodeMutation,
  useVerifyPasswordResetCodeMutation,
  useConfirmPasswordResetMutation,
} = firebaseApi;

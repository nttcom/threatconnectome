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
  setPersistence,
  browserSessionPersistence,
} from "firebase/auth";

import Firebase from "../utils/Firebase";

export const firebaseApi = createApi({
  reducerPath: "firebaseApi",
  baseQuery: fakeBaseQuery(),
  endpoints: (builder) => ({
    /*
    getAccessToken builder.query({
      queryFn: (_, { getState }) => {
        try {
          const data = getState().auth.token;
          if (!data) {
            throw new Error("No access token");
          }
          return { data };
        } catch (error) {
          return { error };
        }
      },
      providesTags: () => [{ type: "Credential" }],
    }),
    */
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
      queryFn: async ({ email, password }) => {
        await setPersistence(Firebase.getAuth(), browserSessionPersistence);
        return await signInWithEmailAndPassword(Firebase.getAuth(), email, password)
          .then((credential) => {
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    signInWithSamlPopup: builder.mutation({
      queryFn: async () => {
        const samlProvider = Firebase.getSamlProvider();
        if (!samlProvider) {
          return { error: "SAML not supported" };
        }
        return await signInWithPopup(Firebase.getAuth(), samlProvider)
          .then((credential) => {
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    createUserWithEmailAndPassword: builder.mutation({
      queryFn: async ({ email, password }) => {
        return await createUserWithEmailAndPassword(Firebase.getAuth(), email, password)
          .then((credential) => {
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    applyActionCode: builder.mutation({
      queryFn: async ({ actionCode }) => {
        return await applyActionCode(Firebase.getAuth(), actionCode)
          .then(() => {
            return { data: { success: true, message: "Action code applied successfully" } };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
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
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    confirmPasswordReset: builder.mutation({
      queryFn: async ({ actionCode, newPassword }) => {
        return await confirmPasswordReset(Firebase.getAuth(), actionCode, newPassword)
          .then(() => {
            return { data: { success: true, message: "Password has been reset successfully" } };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
  }),
});

export const {
  /* useGetAccessTokenQuery, */
  useSendEmailVerificationMutation,
  useSendPasswordResetEmailMutation,
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
  useCreateUserWithEmailAndPasswordMutation,
  useApplyActionCodeMutation,
  useVerifyPasswordResetCodeMutation,
  useConfirmPasswordResetMutation,
} = firebaseApi;

import { createApi, fakeBaseQuery } from "@reduxjs/toolkit/query/react";
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  createUserWithEmailAndPassword,
  applyActionCode,
  verifyPasswordResetCode,
  confirmPasswordReset,
} from "firebase/auth";

import { setAuthToken } from "../slices/auth";
import { auth, samlProvider } from "../utils/firebase";

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
    signInWithEmailAndPassword: builder.mutation({
      queryFn: async ({ email, password }, { dispatch }) => {
        return await signInWithEmailAndPassword(auth, email, password)
          .then((credential) => {
            dispatch(setAuthToken(credential.user.accessToken));
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    signInWithSamlPopup: builder.mutation({
      queryFn: async (_, { dispatch }) => {
        if (!samlProvider) {
          return { error: "SAML not supported" };
        }
        return await signInWithPopup(auth, samlProvider)
          .then((credential) => {
            dispatch(setAuthToken(credential.user.accessToken));
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    createUserWithEmailAndPassword: builder.mutation({
      queryFn: async ({ email, password }) => {
        return await createUserWithEmailAndPassword(auth, email, password)
          .then((credential) => {
            return { data: credential };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    applyActionCode: builder.mutation({
      queryFn: async ({ actionCode }) => {
        return await applyActionCode(auth, actionCode)
          .then(() => {
            return { data: { success: true, message: "Action code applied successfully" } };
          })
          .catch((error) => ({ error }));
      },
      invalidatesTags: () => [{ type: "Credential" }],
    }),
    verifyPasswordResetCode: builder.mutation({
      queryFn: async ({ actionCode }) => {
        return await verifyPasswordResetCode(auth, actionCode)
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
        return await confirmPasswordReset(auth, actionCode, newPassword)
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
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
  useCreateUserWithEmailAndPasswordMutation,
  useApplyActionCodeMutation,
  useVerifyPasswordResetCodeMutation,
  useConfirmPasswordResetMutation,
} = firebaseApi;

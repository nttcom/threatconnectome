import { createApi, fakeBaseQuery } from "@reduxjs/toolkit/query/react";
import {
  sendEmailVerification,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
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
        return await sendPasswordResetEmail(auth, email, actionCodeSettings)
          .then((success) => {
            return { data: success };
          })
          .catch((error) => ({ error }));
      },
    }),
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
  }),
});

export const {
  /* useGetAccessTokenQuery, */
  useSendEmailVerificationMutation,
  useSendPasswordResetEmailMutation,
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
} = firebaseApi;

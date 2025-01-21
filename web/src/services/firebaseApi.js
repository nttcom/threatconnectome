import { createApi, fakeBaseQuery } from "@reduxjs/toolkit/query/react";
import {
  signInWithEmailAndPassword,
  signInWithPopup,
  setPersistence,
  browserSessionPersistence,
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
        await setPersistence(auth, browserSessionPersistence);
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
  useSignInWithEmailAndPasswordMutation,
  useSignInWithSamlPopupMutation,
} = firebaseApi;

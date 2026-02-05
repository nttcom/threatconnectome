import { Link, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";

import { useCreateUserMutation, useTryLoginMutation } from "../../services/tcApi";
import Supabase from "../../utils/Supabase";
import { errorToString } from "../../utils/func";

/* Note: currently, work with supabase only. */
const supabase =
  import.meta.env.VITE_AUTH_SERVICE === "supabase" ? Supabase.getClient() : undefined;

export function AuthKeycloakCallback() {
  const { t } = useTranslation("authKeycloakCallback", { keyPrefix: "AuthKeycloakCallbackPage" });
  const navigate = useNavigate();
  const location = useLocation();
  const [message, setMessage] = useState(t("checkingAuthCode"));
  const redirectedFrom = useSelector((state) => state.auth.redirectedFrom);

  const params = new URLSearchParams(location.search);

  const [tryLogin] = useTryLoginMutation();
  const [createUser] = useCreateUserMutation();

  useEffect(() => {
    const _checkSessionAndNavigateToInternalPage = async () => {
      const navigateTo = {
        pathname: redirectedFrom.from || "/",
        search: redirectedFrom.search ?? "",
      };
      const { data, error } = await supabase.auth.getSession();
      if (!data?.session) {
        console.log(error);
        setMessage(t("cannotGetSession", { error: error?.message }));
        return;
      }
      try {
        await tryLogin()
          .unwrap()
          .catch(async (error) => {
            switch (error.data?.detail) {
              case "No such user": {
                await createUser({ body: {} })
                  .unwrap()
                  .catch((error2) => {
                    throw new Error(t("cannotCreateUser", { error: errorToString(error2) }));
                  });
                if (navigateTo.pathname === "/") {
                  navigateTo.pathname = "/account";
                  navigateTo.search = "";
                }
                break;
              }
              default:
                throw new Error(t("somethingWentWrong", { error: errorToString(error) }));
            }
          });
      } catch (error) {
        setMessage(error.message);
        console.error(error);
        return;
      }
      navigate(navigateTo);
    };
    _checkSessionAndNavigateToInternalPage();
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, []);

  return (
    <>
      <Typography>{message}</Typography>
      <Link href={"/login"}>{t("backToLogin")}</Link>
    </>
  );
}

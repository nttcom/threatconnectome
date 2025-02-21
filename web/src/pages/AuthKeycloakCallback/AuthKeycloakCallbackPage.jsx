import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import Supabase from "../../utils/Supabase";

const supabase =
  import.meta.env.VITE_AUTH_SERVICE === "supabase" ? Supabase.getClient() : undefined;

export function AuthKeycloakCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const [message, setMessage] = useState("Now checking AuthCode...");

  const params = new URLSearchParams(location.search);
  const code = params.get("code");

  useEffect(() => {
    if (!code) {
      //navigate("/login", { state: { message: "AuthError: missing auth code" } });
      setMessage("Missing Auth code");
      return;
    }
    const _verifyCode = async (code) => {
      const { error } = await supabase.auth.exchangeCodeForSession(code);
      if (error) {
        console.log(error);
        setMessage(error.message);
        return;
        //navigate("/login", { state: { message: `AuthCodeError: ${error}` } });
      }
      console.log("auth succeeded!");
      navigate("/");
    };
    _verifyCode(code);
  }, [code, navigate]);

  console.log(params);
  return (
    <>
      <p>code: {code}</p>
      <p>{message}</p>
    </>
  );
}

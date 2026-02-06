import { useMediaQuery } from "@mui/material";
import { useTranslation } from "react-i18next";

import { useTodoState } from "../../hooks/ToDo/useTodoState";
import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useGetUserMeQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { errorToString } from "../../utils/func";

import ToDoCardView from "./ToDoCardView/ToDoCardView";
import { ToDoTableView } from "./ToDoTableView/ToDoTableView";

export function ToDo() {
  const { t } = useTranslation("toDo", { keyPrefix: "ToDoPage" });
  const isMobile = useMediaQuery((theme) => theme.breakpoints.down("md"));

  // All URL state management for the ToDo page is encapsulated in this custom hook.
  // It includes ToDo-specific logic, such as resetting the page on filter/sort changes,
  const { apiParams, ...handlers } = useTodoState();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });

  if (skip) return <></>;
  if (userMeError)
    throw new APIError(errorToString(userMeError), {
      api: "getUserMe",
    });

  if (userMeIsLoading) return <>{t("loadingUserInfo")}</>;
  const pteamIds = userMe?.pteam_roles.map((role) => role.pteam.pteam_id) ?? [];

  return (
    <>
      {isMobile ? (
        <ToDoCardView pteamIds={pteamIds} apiParams={apiParams} {...handlers} />
      ) : (
        <ToDoTableView pteamIds={pteamIds} apiParams={apiParams} {...handlers} />
      )}
    </>
  );
}

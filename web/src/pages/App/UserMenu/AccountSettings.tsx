import { useSnackbar } from "notistack";
import { useTranslation } from "react-i18next";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useUpdateUserMutation } from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";
import type { UserResponse, UserUpdateRequest } from "../../../../types/types.gen";

import { AccountSettingsDialog } from "./AccountSettingsDialog/AccountSettingsDialog";

type AccountSettingsProps = {
  accountSettingOpen: boolean;
  setAccountSettingOpen: (open: boolean) => void;
  userMe: UserResponse;
};

export function AccountSettings({
  accountSettingOpen,
  setAccountSettingOpen,
  userMe,
}: AccountSettingsProps) {
  const { t } = useTranslation("app", { keyPrefix: "UserMenu.AccountSettings" });

  const { enqueueSnackbar } = useSnackbar();
  const [updateUser] = useUpdateUserMutation();
  useSkipUntilAuthUserIsReady();

  const handleUpdateUser = async (request: UserUpdateRequest) => {
    updateUser({
      path: { user_id: userMe.user_id },
      body: request,
    })
      .unwrap()
      .then(() => {
        enqueueSnackbar(t("updateSucceeded"), { variant: "success" });
      })
      .catch((error) => enqueueSnackbar(errorToString(error), { variant: "error" }));
  };

  return (
    <AccountSettingsDialog
      accountSettingOpen={accountSettingOpen}
      setAccountSettingOpen={setAccountSettingOpen}
      onUpdateUser={handleUpdateUser}
      userMe={userMe}
    />
  );
}

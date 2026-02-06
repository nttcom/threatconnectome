import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useUpdateUserMutation } from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";

import { AccountSettingsDialog } from "./AccountSettingsDialog/AccountSettingsDialog";

export function AccountSettings(props) {
  const { accountSettingOpen, setAccountSettingOpen, userMe } = props;
  const { t } = useTranslation("app", { keyPrefix: "UserMenu.AccountSettingsDialog" });

  const { enqueueSnackbar } = useSnackbar();
  const [updateUser] = useUpdateUserMutation();
  const skip = useSkipUntilAuthUserIsReady();

  const handleUpdateUser = async (request) => {
    updateUser({
      path: { user_id: userMe.user_id },
      body: request,
    })
      .unwrap()
      .then((succeeded) => {
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

AccountSettings.propTypes = {
  accountSettingOpen: PropTypes.bool.isRequired,
  setAccountSettingOpen: PropTypes.func.isRequired,
  userMe: PropTypes.object.isRequired,
};

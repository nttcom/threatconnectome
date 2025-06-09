import { useSnackbar } from "notistack";
import PropTypes from "prop-types";

import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import { useUpdateUserMutation } from "../../../services/tcApi";
import { errorToString } from "../../../utils/func";

import { AccountSettingsDialog } from "./AccountSettingsDialog";

export function AccountSettings(props) {
  const { accountSettingOpen, setAccountSettingOpen, userMe } = props;

  const { enqueueSnackbar } = useSnackbar();
  const [updateUser] = useUpdateUserMutation();
  const skip = useSkipUntilAuthUserIsReady();

  const handleSelectYear = async (event) => {
    updateUser({
      userId: userMe.user_id,
      data: { years: event.target.value },
    })
      .unwrap()
      .then((succeeded) => {
        enqueueSnackbar("Update user info succeeded", { variant: "success" });
      })
      .catch((error) => enqueueSnackbar(errorToString(error), { variant: "error" }));
  };

  return (
    <AccountSettingsDialog
      accountSettingOpen={accountSettingOpen}
      setAccountSettingOpen={setAccountSettingOpen}
      onSelectYear={handleSelectYear}
      userMe={userMe}
    />
  );
}

AccountSettings.propTypes = {
  accountSettingOpen: PropTypes.bool.isRequired,
  setAccountSettingOpen: PropTypes.func.isRequired,
  userMe: PropTypes.object.isRequired,
};

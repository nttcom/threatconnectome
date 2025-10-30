import { AccountSettingsDialog } from "./AccountSettingsDialog";

const mockUser = {
  email: "user.single-team@example.com",
  user_id: "user-id-67890",
  years: 5,
  pteam_roles: [{ pteam: { pteam_id: "pteam_charlie", pteam_name: "Charlie Analysis Team" } }],
};

export default {
  title: "Dialogs/AccountSettingsDialog",
  component: AccountSettingsDialog,
  args: {
    accountSettingOpen: true,
    userMe: mockUser,
  },
};

export const Default = {};

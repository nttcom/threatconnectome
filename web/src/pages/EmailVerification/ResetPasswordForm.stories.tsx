import type { Meta } from "@storybook/react-vite";

import { AuthContext, type AuthContextValue } from "../../hooks/auth";
// @ts-expect-error TS7016
import ResetPasswordForm from "./ResetPasswordForm";

const meta = {
  component: ResetPasswordForm,
  parameters: {
    layout: "fullscreen",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ResetPasswordForm>;

export default meta;

export const Default = () => {
  const mockAuthContext = {
    verifyPasswordResetCode: () => Promise.resolve(),
    confirmPasswordReset: () => Promise.resolve("new-verification-id-67890"),
  } as unknown as AuthContextValue;
  const oobCode = "demo-oob-code";

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <ResetPasswordForm oobCode={oobCode} />
    </AuthContext.Provider>
  );
};

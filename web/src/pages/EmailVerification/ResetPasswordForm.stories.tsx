import type { Meta } from "@storybook/react-vite";

// @ts-expect-error TS7016
import { AuthContext } from "../../hooks/auth";
// @ts-expect-error TS7016
import ResetPasswordForm from "./ResetPasswordForm";

const meta = {
  title: "Pages/EmailVerification/ResetPasswordForm",
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
  };
  const oobCode = "demo-oob-code";

  return (
    <AuthContext.Provider value={mockAuthContext}>
      <ResetPasswordForm oobCode={oobCode} />
    </AuthContext.Provider>
  );
};

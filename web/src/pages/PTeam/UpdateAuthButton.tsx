import { Button } from "@mui/material";
import { useTranslation } from "react-i18next";

import dialogStyle from "../../cssModule/dialog.module.css";

type UpdateAuthButtonProps = {
  disabled: boolean;
  onUpdate: () => void;
};

export function UpdateAuthButton(props: UpdateAuthButtonProps) {
  const { disabled, onUpdate } = props;
  const { t } = useTranslation("pteam", { keyPrefix: "UpdateAuthButton" });

  return (
    <Button disabled={disabled} onClick={onUpdate} className={dialogStyle.submit_btn}>
      {t("update")}
    </Button>
  );
}

import AccountCircleIcon from "@mui/icons-material/AccountCircle";

import { IconRenderer } from "./IconRenderer";
import { MenuTriggerButton } from "./MenuTriggerButton";
import { compactTopbarButtonSx } from "./topbarStyles";

export function UserMenuButton({ active, labels, onClick }) {
  const userIcon = <IconRenderer icon={AccountCircleIcon} size={22} />;

  return (
    <MenuTriggerButton
      active={active}
      ariaLabel={labels.userMenu}
      onClick={onClick}
      sx={compactTopbarButtonSx}
    >
      {userIcon}
    </MenuTriggerButton>
  );
}

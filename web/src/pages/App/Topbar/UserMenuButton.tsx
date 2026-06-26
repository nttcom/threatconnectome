import AccountCircleIcon from "@mui/icons-material/AccountCircle";

import { IconRenderer } from "./IconRenderer";
import { MenuTriggerButton } from "./MenuTriggerButton";
import { compactTopbarButtonSx } from "./topbarStyles";
import type { MenuToggleHandler, TopbarLabels } from "./topbarTypes";

type UserMenuButtonProps = {
  active: boolean;
  labels: TopbarLabels;
  onClick: MenuToggleHandler;
};

export function UserMenuButton({ active, labels, onClick }: UserMenuButtonProps) {
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

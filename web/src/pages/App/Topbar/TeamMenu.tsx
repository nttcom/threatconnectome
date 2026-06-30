import { MenuHeader } from "./MenuHeader";
import { MenuShell } from "./MenuShell";
import { TeamMenuList } from "./TeamMenuList";
import { menuWidths } from "./topbarStyles";
import type { MenuAnchor, TopbarLabels, TopbarTeamItem } from "./topbarTypes";

type TeamMenuProps = {
  anchorEl: MenuAnchor;
  labels: TopbarLabels;
  open: boolean;
  onClose: () => void;
  onCreateTeam: () => void;
  onSelectTeam: (teamId: string) => void;
  teamItems: TopbarTeamItem[];
};

export function TeamMenu({
  anchorEl,
  labels,
  open,
  onClose,
  onCreateTeam,
  onSelectTeam,
  teamItems,
}: TeamMenuProps) {
  const closeAfterCreateTeam = () => {
    onCreateTeam();
    onClose();
  };

  const closeAfterSelectTeam = (teamId: string) => {
    onSelectTeam(teamId);
    onClose();
  };

  return (
    <MenuShell
      anchorEl={anchorEl}
      ariaLabel={labels.teamSelect}
      open={open}
      onClose={onClose}
      width={menuWidths.default}
    >
      <MenuHeader title={labels.teamSelect} />
      <TeamMenuList
        labels={labels}
        onCreateTeam={closeAfterCreateTeam}
        onSelectTeam={closeAfterSelectTeam}
        teamItems={teamItems}
      />
    </MenuShell>
  );
}

import { MenuHeader } from "./MenuHeader";
import { MenuShell } from "./MenuShell";
import { TeamMenuList } from "./TeamMenuList";
import { menuWidths } from "./topbarStyles";

export function TeamMenu({
  anchorEl,
  labels,
  open,
  onClose,
  onCreateTeam,
  onSelectTeam,
  teamItems,
}) {
  const closeAfterCreateTeam = () => {
    onCreateTeam();
    onClose();
  };

  const closeAfterSelectTeam = (teamId) => {
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

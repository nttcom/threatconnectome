import "@fontsource/inter/700.css";

import { AppBar, Box, Stack, Toolbar } from "@mui/material";
import PropTypes from "prop-types";

import { useTopbarMenu } from "../../../hooks/App/useTopbarMenu";

import { PageMenu } from "./PageMenu";
import { PageMenuButton } from "./PageMenuButton";
import { TeamMenu } from "./TeamMenu";
import { TeamMenuButton } from "./TeamMenuButton";
import { TopbarLogoLink } from "./TopbarLogoLink";
import { UserMenu } from "./UserMenu";
import { UserMenuButton } from "./UserMenuButton";
import { labelsType, pageItemType, teamItemType } from "./topbarPropTypes";
import { colors } from "./topbarStyles";

export function TopbarView({
  currentPage,
  currentTeam,
  labels,
  languageSwitcher,
  onCreateTeam,
  onLogout,
  onOpenAccountSettings,
  onSelectHome,
  onSelectPage,
  onSelectTeam,
  pageItems,
  teamItems,
}) {
  const { anchorEl, close, toggle, isOpen } = useTopbarMenu();

  return (
    <>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          height: 64,
          bgcolor: "#fff",
          color: colors.ink900,
          borderBottom: `1px solid ${colors.slate200}`,
        }}
      >
        <Toolbar
          sx={{
            minHeight: "64px !important",
            height: 64,
            px: { xs: 2, sm: 3, lg: 4 },
            py: 0,
            gap: { sm: 3 },
            columnGap: { xs: 0.75, sm: 3 },
            alignItems: "center",
            display: { xs: "grid", sm: "flex" },
            gridTemplateColumns: { xs: "40px 40px 1fr 40px 40px", sm: "none" },
          }}
        >
          <Stack
            direction="row"
            sx={{
              display: { xs: "none", sm: "flex" },
              alignItems: "center",
              gap: 3,
              minWidth: 0,
              flex: "1 1 auto",
              height: "100%",
            }}
          >
            <TopbarLogoLink ariaLabel={labels.homeAriaLabel} onClick={onSelectHome} />
            <Box
              sx={{
                display: { xs: "none", sm: "block" },
                width: "1px",
                height: 32,
                flexShrink: 0,
                bgcolor: colors.slate200,
              }}
            />
            <PageMenuButton
              active={isOpen("page")}
              currentPage={currentPage}
              labels={labels}
              onClick={toggle("page")}
            />
          </Stack>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "start" }}>
            <PageMenuButton
              active={isOpen("page")}
              currentPage={currentPage}
              labels={labels}
              onClick={toggle("page")}
            />
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "start" }}>
            <TeamMenuButton
              active={isOpen("team")}
              currentTeam={currentTeam}
              labels={labels}
              onClick={toggle("team")}
            />
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "center" }}>
            <TopbarLogoLink ariaLabel={labels.homeAriaLabel} onClick={onSelectHome} />
          </Box>

          <Stack
            direction="row"
            sx={{
              display: { xs: "none", sm: "flex" },
              alignItems: "center",
              gap: 1.5,
              flexShrink: 0,
              height: "100%",
            }}
          >
            <TeamMenuButton
              active={isOpen("team")}
              currentTeam={currentTeam}
              labels={labels}
              onClick={toggle("team")}
            />
            {languageSwitcher}
            <UserMenuButton active={isOpen("user")} labels={labels} onClick={toggle("user")} />
          </Stack>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "end" }}>
            {languageSwitcher}
          </Box>

          <Box sx={{ display: { xs: "flex", sm: "none" }, justifySelf: "end" }}>
            <UserMenuButton active={isOpen("user")} labels={labels} onClick={toggle("user")} />
          </Box>
        </Toolbar>
      </AppBar>

      <PageMenu
        anchorEl={anchorEl}
        currentPage={currentPage}
        labels={labels}
        open={isOpen("page")}
        onClose={close}
        onSelectPage={onSelectPage}
        pageItems={pageItems}
      />
      <TeamMenu
        anchorEl={anchorEl}
        labels={labels}
        open={isOpen("team")}
        onClose={close}
        onCreateTeam={onCreateTeam}
        onSelectTeam={onSelectTeam}
        teamItems={teamItems}
      />
      <UserMenu
        anchorEl={anchorEl}
        labels={labels}
        open={isOpen("user")}
        onClose={close}
        onLogout={onLogout}
        onOpenAccountSettings={onOpenAccountSettings}
      />
    </>
  );
}

TopbarView.propTypes = {
  currentPage: pageItemType.isRequired,
  currentTeam: teamItemType,
  labels: labelsType.isRequired,
  languageSwitcher: PropTypes.node.isRequired,
  onCreateTeam: PropTypes.func.isRequired,
  onLogout: PropTypes.func.isRequired,
  onOpenAccountSettings: PropTypes.func.isRequired,
  onSelectHome: PropTypes.func.isRequired,
  onSelectPage: PropTypes.func.isRequired,
  onSelectTeam: PropTypes.func.isRequired,
  pageItems: PropTypes.arrayOf(pageItemType).isRequired,
  teamItems: PropTypes.arrayOf(teamItemType).isRequired,
};

TopbarView.defaultProps = {
  currentTeam: null,
};

import { useTranslation } from "react-i18next";

import { LanguageSwitcher } from "../../../components/LanguageSwitcher";
import { useTopbarModel } from "../../../hooks/App/useTopbarModel";
import { buildTopbarPageItems } from "../../../utils/App/topbarNavigation";

import { TopbarView } from "./TopbarView";
import { PTeamCreateModal } from "../PTeamCreateModal";
import { AccountSettings } from "../UserMenu/AccountSettings";

export function Topbar() {
  const { t } = useTranslation("app", { keyPrefix: "Topbar" });
  const labels = {
    current: t("current"),
    currentTeamDetail: t("currentTeamDetail"),
    createTeam: t("createTeam"),
    homeAriaLabel: t("homeAriaLabel"),
    logout: t("logout"),
    noTeam: t("noTeam"),
    pageMenu: t("pageMenu"),
    pageSwitch: t("pageSwitch"),
    settings: t("settings"),
    teamMenu: t("teamMenu"),
    teamSelect: t("teamSelect"),
    userMenu: t("userMenu"),
  };
  const pageItems = buildTopbarPageItems(t);
  const topbar = useTopbarModel({ labels, pageItems });

  return (
    <>
      <TopbarView
        currentPage={topbar.currentPage}
        currentTeam={topbar.currentTeam}
        hasUserMe={topbar.hasUserMe}
        labels={topbar.labels}
        languageSwitcher={<LanguageSwitcher />}
        onCreateTeam={topbar.onCreateTeam}
        onLogout={topbar.onLogout}
        onOpenAccountSettings={topbar.onOpenAccountSettings}
        onSelectHome={topbar.onSelectHome}
        onSelectPage={topbar.onSelectPage}
        onSelectTeam={topbar.onSelectTeam}
        pageItems={topbar.pageItems}
        teamItems={topbar.teamItems}
      />
      {topbar.userMe ? (
        <AccountSettings
          accountSettingOpen={topbar.accountSettingOpen}
          setAccountSettingOpen={topbar.setAccountSettingOpen}
          userMe={topbar.userMe}
        />
      ) : null}
      <PTeamCreateModal
        open={topbar.teamCreationOpen}
        onSetOpen={topbar.setTeamCreationOpen}
        onCloseTeamSelector={() => undefined}
      />
    </>
  );
}

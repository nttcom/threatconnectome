import { useTranslation } from "react-i18next";

import { LanguageSwitcher } from "../../components/LanguageSwitcher";

import { PTeamCreateModal } from "./PTeamCreateModal";
import { TopbarView } from "./TopbarView";
import { AccountSettings } from "./UserMenu/AccountSettings";
import { buildTopbarPageItems } from "./topbarNavigation";
import { useTopbarModel } from "./useTopbarModel";

export function Topbar() {
  const { t } = useTranslation("app", { keyPrefix: "Topbar" });
  const labels = {
    current: t("current"),
    currentTeamDetail: t("currentTeamDetail"),
    createTeam: t("createTeam"),
    homeAriaLabel: t("homeAriaLabel"),
    loadingUserInfo: t("loadingUserInfo"),
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
        labels={topbar.labels}
        languageSwitcher={<LanguageSwitcher />}
        loading={topbar.loading}
        onCreateTeam={topbar.onCreateTeam}
        onLogout={topbar.onLogout}
        onOpenAccountSettings={topbar.onOpenAccountSettings}
        onSelectHome={topbar.onSelectHome}
        onSelectPage={topbar.onSelectPage}
        onSelectTeam={topbar.onSelectTeam}
        pageItems={topbar.pageItems}
        teamItems={topbar.teamItems}
        userEmail={topbar.userMe?.email}
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

import CheckIcon from "@mui/icons-material/Check";
import EditIcon from "@mui/icons-material/Edit";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import { Card, Stack } from "@mui/material";
import { useTranslation } from "react-i18next";

import { DeploymentsContent } from "./DeploymentsContent";
import { AccordionHeader, CountBadge, HeaderActionButton } from "./sharedUiParts";
import { statusCardSx } from "./styleTokens";
import type { SbomServicePatch } from "./SBOMManagementTypes";

export function DeploymentsPanel({
  ipAddresses,
  countryCode,
  address,
  editing,
  onCommit,
  onToggle,
  onUpdate,
  open,
}: {
  ipAddresses: string[];
  countryCode: string;
  address: string;
  editing: boolean;
  onCommit: () => void;
  onToggle: () => void;
  onUpdate: (patch: SbomServicePatch) => void;
  open: boolean;
}) {
  const { t } = useTranslation("status", { keyPrefix: "DeploymentsPanel" });

  return (
    <Card
      sx={{
        ...statusCardSx,
      }}
    >
      <AccordionHeader
        action={
          <Stack direction="row" alignItems="center" sx={{ gap: 1, height: 32 }}>
            <CountBadge>{t("countItems", { count: ipAddresses.length })}</CountBadge>
            <HeaderActionButton
              active={editing}
              icon={editing ? CheckIcon : EditIcon}
              onClick={onCommit}
            >
              {editing ? t("done") : t("edit")}
            </HeaderActionButton>
          </Stack>
        }
        icon={StorageRoundedIcon}
        onToggle={onToggle}
        open={open}
        title={t("deployments")}
      />
      <DeploymentsContent
        ipAddresses={ipAddresses}
        countryCode={countryCode}
        address={address}
        editing={editing}
        onUpdate={onUpdate}
        open={open}
      />
    </Card>
  );
}

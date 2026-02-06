import { Box, Grid } from "@mui/material";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { VulnSSVCElement } from "./VulnSSVCElement";

export function VulnSSVCCards(props) {
  const { exploitation, automatable } = props;
  const { t } = useTranslation("vulnDetail", { keyPrefix: "VulnSSVCCards" });

  const automatableDescription = {
    title: t("automatable.title"),
    titleDescription: t("automatable.titleDescription"),
    values: [
      {
        key: "no",
        name: t("automatable.no.name"),
        valueDescription: t("automatable.no.valueDescription"),
      },
      {
        key: "yes",
        name: t("automatable.yes.name"),
        valueDescription: t("automatable.yes.valueDescription"),
      },
    ],
  };

  const exploitationDescription = {
    title: t("exploitation.title"),
    titleDescription: t("exploitation.titleDescription"),
    values: [
      {
        key: "none",
        name: t("exploitation.none.name"),
        valueDescription: t("exploitation.none.valueDescription"),
      },
      {
        key: "public_poc",
        name: t("exploitation.public_poc.name"),
        valueDescription: t("exploitation.public_poc.valueDescription"),
      },
      {
        key: "active",
        name: t("exploitation.active.name"),
        valueDescription: t("exploitation.active.valueDescription"),
      },
    ],
  };

  return (
    <Box sx={{ m: 1 }}>
      <Grid container spacing={1}>
        <VulnSSVCElement
          title={automatableDescription.title}
          titleDescription={automatableDescription.titleDescription}
          values={automatableDescription.values}
          value={automatable}
        />
        <VulnSSVCElement
          title={exploitationDescription.title}
          titleDescription={exploitationDescription.titleDescription}
          values={exploitationDescription.values}
          value={exploitation}
        />
      </Grid>
    </Box>
  );
}
VulnSSVCCards.propTypes = {
  exploitation: PropTypes.string.isRequired,
  automatable: PropTypes.string.isRequired,
};

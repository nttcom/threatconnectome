import { Box, Grid } from "@mui/material";
import PropTypes from "prop-types";

import { VulnSSVCElement } from "./VulnSSVCElement";

export function VulnSSVCCards(props) {
  const { exploitation, automatable } = props;

  const automatableDescription = {
    title: "Automatable",
    titleDescription:
      "Can an attacker reliably automate creating exploitation events for this vulnerability?",
    values: [
      {
        key: "no",
        name: "No",
        valueDescription:
          "No: Attackers cannot reliably automate steps 1-4 of the kill chain for this vulnerability. These steps are (1) reconnaissance, (2) weaponization, (3) delivery, and (4) exploitation.",
      },
      {
        key: "yes",
        name: "Yes",
        valueDescription: "Yes: Attackers can reliably automate steps 1-4 of the kill chain.",
      },
    ],
  };

  const exploitationDescription = {
    title: "Exploitation",
    titleDescription: "The present state of exploitation of the vulnerability.",
    values: [
      {
        key: "none",
        name: "None",
        valueDescription:
          "None: There is no evidence of active exploitation and no public proof of concept (PoC) of how to exploit the vulnerability.",
      },
      {
        key: "public_poc",
        name: "Public PoC",
        valueDescription:
          "Public PoC: One of the following is true: (1) Typical public PoC exists in sources such as Metasploit or websites like ExploitDB; or (2) the vulnerability has a well-known method of exploitation.",
      },
      {
        key: "active",
        name: "Active",
        valueDescription:
          "Active: Shared, observable, reliable evidence that the exploit is being used in the wild by real attackers; there is credible public reporting.",
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

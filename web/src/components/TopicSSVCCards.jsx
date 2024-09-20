import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import {
  Box,
  Card,
  Grid,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Typography,
} from "@mui/material";
import PropTypes from "prop-types";
import React from "react";

function TopicSSVCElement(props) {
  const { title, titleDescription, values, value } = props;

  return (
    <Grid key={title} item xs={6}>
      <Card variant="outlined" sx={{ p: 3, height: "100%" }}>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            mb: 1,
          }}
        >
          <Typography sx={{ fontWeight: "bold", pr: 0.5 }}>{title}</Typography>
          <Tooltip title={titleDescription}>
            <HelpOutlineOutlinedIcon color="action" fontSize="small" />
          </Tooltip>
        </Box>
        <ToggleButtonGroup
          color="primary"
          value={values.filter((item) => value === item.key)[0].key}
          sx={{ mb: 1 }}
        >
          {values.map((value) => (
            <ToggleButton key={value.key} value={value.key} disabled>
              {value.name}
            </ToggleButton>
          ))}
        </ToggleButtonGroup>
        <Typography variant="body2" color="textSecondary">
          {values.filter((item) => value === item.key)[0].valueDescription}
        </Typography>
      </Card>
    </Grid>
  );
}
TopicSSVCElement.propTypes = {
  title: PropTypes.string.isRequired,
  titleDescription: PropTypes.string.isRequired,
  values: PropTypes.array.isRequired,
  value: PropTypes.string.isRequired,
};

export function TopicSSVCCards(props) {
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
        <TopicSSVCElement
          title={automatableDescription.title}
          titleDescription={automatableDescription.titleDescription}
          values={automatableDescription.values}
          value={automatable}
        />
        <TopicSSVCElement
          title={exploitationDescription.title}
          titleDescription={exploitationDescription.titleDescription}
          values={exploitationDescription.values}
          value={exploitation}
        />
      </Grid>
    </Box>
  );
}
TopicSSVCCards.propTypes = {
  exploitation: PropTypes.string.isRequired,
  automatable: PropTypes.string.isRequired,
};

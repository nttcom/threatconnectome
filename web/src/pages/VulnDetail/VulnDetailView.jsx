import {
  KeyboardArrowUp as KeyboardArrowUpIcon,
  KeyboardArrowDown as KeyboardArrowDownIcon,
} from "@mui/icons-material";
import { Badge, Box, Button, Card, Chip, MenuItem, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { useState } from "react";

import { ActionTypeIcon } from "../../components/ActionTypeIcon";
import { PackageView } from "../../components/PackageView";

import { VulnCVSSCard } from "./VulnCVSSCard";
import { VulnSSVCCards } from "./VulnSSVCCards";

const packageChip = (chipNumber) => {
  const packageMax = 99;
  return chipNumber <= packageMax ? chipNumber : `${packageMax}+`;
};

export function VulnDetailView(props) {
  const { vuln, actions } = props;

  const [showAllPackages, setShowAllPackages] = useState(false);

  return (
    <>
      <Box>
        <VulnCVSSCard vuln={vuln} />
        {/* Package */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Typography sx={{ fontWeight: "bold" }}>Package</Typography>
            {vuln.vulnerable_packages
              .filter((_, index) => (showAllPackages ? true : index === 0))
              .map((vulnPackage) => (
                <PackageView key={vulnPackage.package_id} vulnPackage={vulnPackage} />
              ))}
            {/* hide or more button if needed */}
            {vuln.vulnerable_packages.length > 1 && (
              <Box display="flex" justifyContent="center" sx={{ mr: 3 }}>
                {showAllPackages ? (
                  <Button
                    onClick={() => setShowAllPackages(false)}
                    variant="outlined"
                    size="small"
                    sx={{ textTransform: "none", width: 120 }}
                  >
                    <KeyboardArrowUpIcon sx={{ ml: -1 }} />
                    Hide
                  </Button>
                ) : (
                  <Badge
                    badgeContent={packageChip(vuln.vulnerable_packages.length - 1)}
                    color="primary"
                    sx={{ mt: 1 }}
                  >
                    <Button
                      onClick={() => setShowAllPackages(true)}
                      variant="outlined"
                      size="small"
                      sx={{ textTransform: "none", width: 120 }}
                    >
                      <KeyboardArrowDownIcon sx={{ ml: -1 }} />
                      More
                    </Button>
                  </Badge>
                )}
              </Box>
            )}
          </Box>
        </Card>
        {/* SSVC decision points */}
        <VulnSSVCCards exploitation={vuln.exploitation} automatable={vuln.automatable} />
        {/* CVE ID */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>CVE ID</Typography>
            </Box>
            {vuln.cve_id === null ? (
              <Typography sx={{ margin: 1 }}>No Known CVE</Typography>
            ) : (
              <Box sx={{ mt: 1 }}>
                <Chip
                  key={vuln.cve_id}
                  label={vuln.cve_id}
                  size="small"
                  sx={{ m: 0.5, borderRadius: 0.5 }}
                />
              </Box>
            )}
          </Box>
        </Card>
        {/* VulnActions */}
        <Card variant="outlined" sx={{ margin: 1 }}>
          <Box sx={{ margin: 3 }}>
            <Box alignItems="center" display="flex" flexDirection="row">
              <Typography sx={{ fontWeight: "bold" }}>Action</Typography>
            </Box>
            {actions.length === 0 ? (
              <Typography sx={{ margin: 1 }}>No data</Typography>
            ) : (
              <>
                <Box>
                  {actions.map((action) => (
                    <MenuItem
                      key={action.action_id}
                      sx={{
                        alignItems: "center",
                        display: "flex",
                        flexDirection: "row",
                      }}
                    >
                      <ActionTypeIcon actionType="elimination" disabled={false} />
                      <Box display="flex" flexDirection="column">
                        <Typography noWrap variant="body">
                          {action.action}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Box>
              </>
            )}
          </Box>
        </Card>
        {/* Other vuln info */}
        <Card variant="outlined" sx={{ margin: 1, mb: 3 }}>
          <Box sx={{ margin: 3 }}>
            <Box display="flex" flexDirection="column">
              <Typography sx={{ fontWeight: "bold" }}>Creator</Typography>
              <Typography>{vuln.created_by}</Typography>
              {/* TODO: convert to email address? */}
            </Box>
            <Box display="flex" flexDirection="column" sx={{ mt: 1 }}>
              <Typography sx={{ fontWeight: "bold" }}>Last Updated</Typography>
              <Typography>{vuln.updated_at}</Typography>
            </Box>
            <Box display="flex" flexDirection="column" sx={{ mt: 1 }}>
              <Typography sx={{ fontWeight: "bold" }}>Vuln ID</Typography>
              <Typography>{vuln.vuln_id}</Typography>
            </Box>
          </Box>
        </Card>
      </Box>
    </>
  );
}
VulnDetailView.propTypes = {
  vuln: PropTypes.object.isRequired,
  actions: PropTypes.array.isRequired,
};

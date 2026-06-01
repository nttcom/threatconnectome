/* eslint-disable react/prop-types */
import AddIcon from "@mui/icons-material/Add";
import CheckIcon from "@mui/icons-material/Check";
import CloseIcon from "@mui/icons-material/Close";
import EditIcon from "@mui/icons-material/Edit";
import LocationOnIcon from "@mui/icons-material/LocationOn";
import StorageRoundedIcon from "@mui/icons-material/StorageRounded";
import { Box, Card, CardContent, IconButton, Stack, TextField, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import { AccordionHeader, CountBadge, HeaderActionButton } from "./sharedUiParts";
import { fieldSx, slate } from "./styleTokens";

function DeploymentList({ deployments, editing, onRemove, onUpdate, open }) {
  const { t } = useTranslation("status", { keyPrefix: "DeploymentsPanel" });
  const display = { md: "block", xs: open ? "block" : "none" };

  return (
    <CardContent sx={{ display, minWidth: 0, pb: 1.5, pt: 0, px: 2 }}>
      <Stack sx={{ gap: 1.5 }}>
        {deployments.length > 0 ? (
          deployments.map((deployment, index) => (
            <Box
              key={deployment.id}
              sx={{
                bgcolor: slate[50],
                border: `1px solid ${slate[200]}`,
                borderRadius: 4,
                p: 1.5,
              }}
            >
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                sx={{ mb: 1.25 }}
              >
                <Typography sx={{ color: slate[700], fontSize: 14, fontWeight: 700 }}>
                  {t("deploymentN", { n: index + 1 })}
                </Typography>
                {editing && (
                  <IconButton
                    aria-label={t("removeDeployment")}
                    onClick={() => onRemove(deployment.id)}
                    size="small"
                    sx={{ color: slate[400], "&:hover": { bgcolor: "white", color: slate[900] } }}
                  >
                    <CloseIcon sx={{ fontSize: 18 }} />
                  </IconButton>
                )}
              </Stack>
              {editing ? (
                <Stack sx={{ gap: 1.25 }}>
                  <TextField
                    fullWidth
                    onChange={(event) => onUpdate(deployment.id, { ip: event.target.value })}
                    placeholder={t("ipAddress")}
                    sx={fieldSx}
                    value={deployment.ip}
                  />
                  <TextField
                    disabled
                    fullWidth
                    placeholder={t("location")}
                    sx={fieldSx}
                    value={deployment.location}
                  />
                </Stack>
              ) : (
                <Stack sx={{ gap: 1.25 }}>
                  <Box>
                    <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                      {t("ipAddress")}
                    </Typography>
                    <Typography sx={{ color: slate[800], fontSize: 14, fontWeight: 600, mt: 0.5 }}>
                      {deployment.ip || (
                        <Box component="span" sx={{ color: slate[400] }}>
                          {t("notSet")}
                        </Box>
                      )}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography sx={{ color: slate[500], fontSize: 12, fontWeight: 700 }}>
                      {t("location")}
                    </Typography>
                    <Stack
                      direction="row"
                      alignItems="center"
                      sx={{ color: slate[800], fontSize: 14, fontWeight: 600, gap: 1, mt: 0.5 }}
                    >
                      <LocationOnIcon sx={{ color: slate[400], fontSize: 18 }} />
                      <Typography
                        component="span"
                        sx={{ color: "inherit", fontSize: 14, fontWeight: 600 }}
                      >
                        {deployment.location || (
                          <Box component="span" sx={{ color: slate[400] }}>
                            {t("notSet")}
                          </Box>
                        )}
                      </Typography>
                    </Stack>
                  </Box>
                </Stack>
              )}
            </Box>
          ))
        ) : (
          <Box
            sx={{
              border: `1px dashed ${slate[300]}`,
              borderRadius: 4,
              color: slate[500],
              fontSize: 14,
              p: 2.5,
              textAlign: "center",
            }}
          >
            {t("noDeployments")}
          </Box>
        )}
      </Stack>
    </CardContent>
  );
}

export function DeploymentsPanel({
  deployments,
  editing,
  onAdd,
  onCommit,
  onRemove,
  onToggle,
  onUpdate,
  open,
}) {
  const { t } = useTranslation("status", { keyPrefix: "DeploymentsPanel" });

  return (
    <Card
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 6,
        boxShadow: "none",
        minWidth: 0,
      }}
    >
      <AccordionHeader
        action={
          <Stack direction="row" alignItems="center" sx={{ gap: 1, height: 32 }}>
            <CountBadge>{t("countItems", { count: deployments.length })}</CountBadge>
            {editing && (
              <HeaderActionButton
                icon={AddIcon}
                onClick={onAdd}
                sx={{
                  display: {
                    md: "inline-flex",
                    xs: open ? "inline-flex" : "none",
                  },
                }}
              >
                {t("add")}
              </HeaderActionButton>
            )}
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
      <DeploymentList
        deployments={deployments}
        editing={editing}
        onRemove={onRemove}
        onUpdate={onUpdate}
        open={open}
      />
    </Card>
  );
}

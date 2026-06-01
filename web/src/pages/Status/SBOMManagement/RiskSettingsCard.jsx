/* eslint-disable react/prop-types */
import CheckIcon from "@mui/icons-material/Check";
import EditIcon from "@mui/icons-material/Edit";
import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { HeaderActionButton } from "./sharedUiParts";
import { labelSx, sectionTitleTextSx, slate } from "./styleTokens";

function ImpactOptionButton({ onSelect, option, selected }) {
  return (
    <Box
      aria-pressed={selected}
      component="button"
      onClick={() => onSelect(option.value)}
      sx={{
        "&:hover": {
          bgcolor: selected ? "#eef6ff" : slate[50],
          borderColor: selected ? "#2563eb" : slate[300],
        },
        alignItems: "stretch",
        bgcolor: selected ? "#eef6ff" : "white",
        border: "1px solid",
        borderColor: selected ? "#2563eb" : slate[200],
        borderRadius: 4,
        boxShadow: selected ? "0 1px 2px rgba(37, 99, 235, 0.14)" : "none",
        color: slate[800],
        cursor: "pointer",
        display: "flex",
        flexDirection: "column",
        font: "inherit",
        minHeight: 104,
        p: 1.5,
        textAlign: "left",
        transition: "background-color 160ms ease, border-color 160ms ease, box-shadow 160ms ease",
        width: "100%",
      }}
      type="button"
    >
      <Stack direction="row" alignItems="flex-start" sx={{ gap: 1, minWidth: 0 }}>
        <Box sx={{ minWidth: 0 }}>
          <Typography
            component="span"
            sx={{
              color: selected ? "#1d4ed8" : slate[700],
              display: "block",
              fontSize: 12,
              fontWeight: 800,
              lineHeight: "16px",
              overflowWrap: "anywhere",
            }}
          >
            {option.label}
          </Typography>
        </Box>
        <Box
          sx={{
            alignItems: "center",
            bgcolor: selected ? "#2563eb" : slate[100],
            border: `1px solid ${selected ? "#2563eb" : slate[200]}`,
            borderRadius: 999,
            color: selected ? "white" : "transparent",
            display: "flex",
            flexShrink: 0,
            height: 22,
            justifyContent: "center",
            ml: "auto",
            width: 22,
          }}
        >
          {selected && <CheckIcon sx={{ display: "block", fontSize: 16 }} />}
        </Box>
      </Stack>
      <Typography
        sx={{
          color: slate[800],
          fontSize: 13,
          fontWeight: 700,
          lineHeight: "20px",
          mt: 1,
          overflowWrap: "anywhere",
        }}
      >
        {option.description}
      </Typography>
    </Box>
  );
}

function ServiceImpactOptionGroup({ description, onSelect, options, selectedValue, title }) {
  return (
    <Box>
      <Typography sx={{ ...labelSx, color: slate[700] }}>{title}</Typography>
      <Typography sx={{ color: slate[500], fontSize: 13, lineHeight: "20px", mt: 0.5 }}>
        {description}
      </Typography>
      <Box
        sx={{
          display: "grid",
          gap: 1,
          gridTemplateColumns: {
            sm: "repeat(auto-fit, minmax(180px, 1fr))",
            xs: "1fr",
          },
          mt: 1.25,
        }}
      >
        {options.map((option) => (
          <ImpactOptionButton
            key={option.value}
            onSelect={onSelect}
            option={option}
            selected={option.value === selectedValue}
          />
        ))}
      </Box>
    </Box>
  );
}

function getImpactOption(options, value) {
  return options.find((option) => option.value === value) || options[0];
}

function ServiceImpactSummaryRow({ option, summaryLabel, title }) {
  return (
    <Box
      sx={{
        bgcolor: slate[50],
        border: `1px solid ${slate[200]}`,
        borderRadius: 4,
        minWidth: 0,
        p: 1.5,
      }}
    >
      <Stack
        direction="row"
        alignItems="baseline"
        flexWrap="wrap"
        sx={{ columnGap: 1, rowGap: 0.5 }}
      >
        <Typography
          component="span"
          sx={{ color: slate[500], fontSize: 12, fontWeight: 800, lineHeight: "16px" }}
        >
          {title}
        </Typography>
        <Typography
          component="span"
          sx={{
            color: slate[800],
            fontSize: 13,
            fontWeight: 800,
            lineHeight: "18px",
            overflowWrap: "anywhere",
          }}
        >
          {option.label}
        </Typography>
      </Stack>
      <Stack direction="row" flexWrap="wrap" sx={{ columnGap: 0.75, mt: 0.75, rowGap: 0.25 }}>
        <Typography
          component="span"
          sx={{
            color: slate[500],
            flexShrink: 0,
            fontSize: 13,
            fontWeight: 800,
            lineHeight: "20px",
          }}
        >
          {summaryLabel}:
        </Typography>
        <Typography
          component="span"
          sx={{
            color: slate[700],
            fontSize: 14,
            fontWeight: 700,
            lineHeight: "20px",
            minWidth: 0,
            overflowWrap: "anywhere",
          }}
        >
          {option.summary}
        </Typography>
      </Stack>
    </Box>
  );
}

export function RiskSettingsCard({ onSave, sbom }) {
  const { t } = useTranslation("status", { keyPrefix: "RiskSettingsCard" });
  const currentSystemExposure = sbom?.systemExposure || "open";
  const currentMissionImpact = sbom?.missionImpact || "mission_failure";
  const systemExposureOptions = [
    {
      description: t("systemExposureSmallDescription"),
      label: t("small"),
      summary: t("systemExposureSmallSummary"),
      value: "small",
    },
    {
      description: t("systemExposureControlledDescription"),
      label: t("controlled"),
      summary: t("systemExposureControlledSummary"),
      value: "controlled",
    },
    {
      description: t("systemExposureOpenDescription"),
      label: t("open"),
      summary: t("systemExposureOpenSummary"),
      value: "open",
    },
  ];
  const missionImpactOptions = [
    {
      description: t("missionImpactDegradedDescription"),
      label: t("degraded"),
      summary: t("missionImpactDegradedSummary"),
      value: "degraded",
    },
    {
      description: t("missionImpactSupportCrippledDescription"),
      label: t("missionImpactSupportCrippled"),
      summary: t("missionImpactSupportCrippledSummary"),
      value: "mef_support_crippled",
    },
    {
      description: t("missionImpactFailureDescription"),
      label: t("missionImpactFailure"),
      summary: t("missionImpactFailureSummary"),
      value: "mef_failure",
    },
    {
      description: t("missionImpactMissionFailureDescription"),
      label: t("missionImpactMissionFailure"),
      summary: t("missionImpactMissionFailureSummary"),
      value: "mission_failure",
    },
  ];
  const [systemExposure, setSystemExposure] = useState(currentSystemExposure);
  const [missionImpact, setMissionImpact] = useState(currentMissionImpact);
  const [editing, setEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const selectedSystemExposure = getImpactOption(systemExposureOptions, systemExposure);
  const selectedMissionImpact = getImpactOption(missionImpactOptions, missionImpact);

  useEffect(() => {
    setSystemExposure(currentSystemExposure);
    setMissionImpact(currentMissionImpact);
    setEditing(false);
    setIsSaving(false);
  }, [currentMissionImpact, currentSystemExposure, sbom?.id]);

  const handleActionClick = async () => {
    if (!editing) {
      setEditing(true);
      return;
    }

    if (systemExposure === currentSystemExposure && missionImpact === currentMissionImpact) {
      setEditing(false);
      return;
    }

    setIsSaving(true);
    try {
      const saved = await onSave?.({ missionImpact, systemExposure });
      if (saved !== false) {
        setSystemExposure(currentSystemExposure);
        setMissionImpact(currentMissionImpact);
        setEditing(false);
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <Card
      sx={{
        border: `1px solid ${slate[200]}`,
        borderRadius: 6,
        boxShadow: "none",
        minWidth: 0,
      }}
    >
      <CardContent sx={{ minWidth: 0, p: 2 }}>
        <Stack sx={{ gap: 1.5 }}>
          <Box
            sx={{
              alignItems: "center",
              display: "flex",
              gap: 1,
              justifyContent: "space-between",
              minWidth: 0,
            }}
          >
            <Typography sx={sectionTitleTextSx}>{t("riskSettings")}</Typography>
            <HeaderActionButton
              active={editing}
              icon={editing ? CheckIcon : EditIcon}
              disabled={isSaving}
              onClick={handleActionClick}
            >
              {editing ? t("done") : t("edit")}
            </HeaderActionButton>
          </Box>
          {editing ? (
            <Stack sx={{ gap: 2 }}>
              <ServiceImpactOptionGroup
                description={t("systemExposureDescription")}
                onSelect={setSystemExposure}
                options={systemExposureOptions}
                selectedValue={systemExposure}
                title={t("systemExposureTitle")}
              />
              <ServiceImpactOptionGroup
                description={t("missionImpactDescription")}
                onSelect={setMissionImpact}
                options={missionImpactOptions}
                selectedValue={missionImpact}
                title={t("missionImpactTitle")}
              />
            </Stack>
          ) : (
            <Stack sx={{ gap: 1 }}>
              <ServiceImpactSummaryRow
                option={selectedSystemExposure}
                summaryLabel={t("systemExposureSummaryLabel")}
                title={t("systemExposureTitle")}
              />
              <ServiceImpactSummaryRow
                option={selectedMissionImpact}
                summaryLabel={t("missionImpactSummaryLabel")}
                title={t("missionImpactTitle")}
              />
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

import { Delete as DeleteIcon } from "@mui/icons-material";
import { Box, IconButton, Tooltip, Typography } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";

import { dateTimeFormat } from "../utils/func";

import ActionTypeIcon from "./ActionTypeIcon";
import UUIDTypography from "./UUIDTypography";

export default function ActionItem(props) {
  const {
    action,
    actionId,
    actionType,
    createdAt,
    recommended,
    zones,
    ext,
    focusTags,
    onChangeRecommended,
    onDelete,
    sx,
  } = props;

  const dustbox = onDelete ? (
    <IconButton
      onClick={() =>
        onDelete({
          action: action,
          action_type: actionType,
          recommended: !recommended,
        })
      }
      size="small"
      sx={{ p: 0 }}
    >
      <DeleteIcon />
    </IconButton>
  ) : (
    <></>
  );

  const actionIcon = <ActionTypeIcon disabled={!recommended} actionType={actionType} />;
  const actionTypeButton = onChangeRecommended ? (
    <IconButton
      onClick={() =>
        onChangeRecommended({
          action: action,
          action_type: actionType,
          recommended: !recommended,
          zones: zones,
          ext: ext,
        })
      }
      size="small"
      sx={{ p: 0 }}
    >
      {actionIcon}
    </IconButton>
  ) : (
    <>{actionIcon}</>
  );
  const decoratedAction = recommended ? (
    <Tooltip arrow placement="bottom" title="recommended">
      {actionTypeButton}
    </Tooltip>
  ) : (
    <>{actionTypeButton}</>
  );
  const extInfo = ext?.tags ? (
    ext.tags.map((tag) => (
      <Box key={tag}>
        <Typography
          color={grey[600]}
          variant="caption"
          sx={focusTags?.includes(tag) ? { fontWeight: 900 } : {}}
        >
          Tag: {tag} <br />
        </Typography>
        {ext.vulnerable_versions?.[tag]?.length > 0 && (
          <Typography color={grey[600]} variant="caption" sx={{ ml: 2 }}>
            Vulnerables: {ext.vulnerable_versions?.[tag].join(" || ")}
          </Typography>
        )}
      </Box>
    ))
  ) : (
    <></>
  );
  const zonesInfo = !(zones && zones?.length > 0) ? (
    <></>
  ) : (
    <Typography color={grey[600]} variant="caption">
      Zones:{" "}
      {typeof zones?.[0] === "string"
        ? zones.join(", ")
        : zones.map((zone) => zone.zone_name).join(", ")}
    </Typography>
  );

  return (
    <>
      <Box display="flex" flexDirection="row" alignItems="flex-start" sx={{ mb: 1, ...sx }}>
        {dustbox}
        {decoratedAction}
        <Box display="flex" flexDirection="column">
          <Typography>{action}</Typography>
          {extInfo}
          {zonesInfo}
          <UUIDTypography>{actionId}</UUIDTypography>
          <Typography variant="caption" color={grey[600]}>
            {dateTimeFormat(createdAt)}
          </Typography>
        </Box>
      </Box>
    </>
  );
}

ActionItem.propTypes = {
  action: PropTypes.string.isRequired,
  actionId: PropTypes.string,
  actionType: PropTypes.string.isRequired,
  createdAt: PropTypes.string,
  recommended: PropTypes.bool,
  zones: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.string),
    PropTypes.arrayOf(PropTypes.object),
  ]),
  ext: PropTypes.object,
  focusTags: PropTypes.arrayOf(PropTypes.string),
  onChangeRecommended: PropTypes.func,
  onDelete: PropTypes.func,
  sx: PropTypes.object,
};
ActionItem.defaultProps = {
  recommended: false,
};

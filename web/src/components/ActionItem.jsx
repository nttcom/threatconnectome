import { Delete as DeleteIcon } from "@mui/icons-material";
import { Box, IconButton, Tooltip, Typography, ListItem, ListItemText } from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";

import { dateTimeFormat } from "../utils/func";

import { ActionTypeIcon } from "./ActionTypeIcon";
import { UUIDTypography } from "./UUIDTypography";

export function ActionItem(props) {
  const {
    action,
    actionId,
    actionType,
    createdAt,
    recommended,
    ext,
    focusTags,
    onChangeRecommended,
    onDelete,
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

  return (
    <>
      <ListItem alignItems="flex-start" disablePadding>
        {decoratedAction}
        <Box flexDirection="column">
          <ListItemText
            primary={action}
            primaryTypographyProps={{
              style: {
                whiteSpace: "normal",
                overflow: "auto",
                width: "100%",
              },
            }}
          />
          <Typography
            sx={{ display: "inline" }}
            component="span"
            variant="body2"
            color="text.primary"
          >
            <Box display="flex" flexDirection="column">
              {extInfo}
              <UUIDTypography>{actionId}</UUIDTypography>
              <Typography color={grey[600]} variant="caption">
                {dateTimeFormat(createdAt)}
              </Typography>
            </Box>
          </Typography>
          {dustbox}
        </Box>
      </ListItem>
    </>
  );
}

ActionItem.propTypes = {
  action: PropTypes.string.isRequired,
  actionId: PropTypes.string,
  actionType: PropTypes.string.isRequired,
  createdAt: PropTypes.string,
  recommended: PropTypes.bool,
  ext: PropTypes.object,
  focusTags: PropTypes.arrayOf(PropTypes.string),
  onChangeRecommended: PropTypes.func,
  onDelete: PropTypes.func,
  sx: PropTypes.object,
};
ActionItem.defaultProps = {
  recommended: false,
};

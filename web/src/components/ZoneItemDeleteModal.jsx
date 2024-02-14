import { Box, Button, Dialog, DialogContent, DialogTitle, Typography } from "@mui/material";
import { red } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import React from "react";
import { useDispatch } from "react-redux";

import { getGTeamZonesSummary } from "../slices/gteam";
import {
  deleteAction,
  deleteTopic,
  deleteZoneFromPTeam,
  updateAction,
  updateTopic,
} from "../utils/api";
import { modalCommonButtonStyle } from "../utils/const";

export function ZoneItemDeleteModal(props) {
  const { onSetShow, show, zone, itemType, itemId } = props;
  const dispatch = useDispatch();
  const { enqueueSnackbar } = useSnackbar();

  if (!show || !zone || !itemType || !itemId) return <></>;
  if (!["topic", "action", "PTeam"].includes(itemType)) {
    alert("Implementation Error");
    return <></>;
  }

  const handleClose = () => onSetShow(false);

  const itemProp =
    itemType === "topic"
      ? {
          itemList: zone.topics,
          idKey: "topic_id",
          nameKey: "title",
        }
      : itemType === "action"
        ? {
            itemList: zone.actions,
            idKey: "action_id",
            nameKey: "action",
          }
        : {
            itemList: zone.pteams,
            idKey: "pteam_id",
            nameKey: "pteam_name",
          };
  const target = itemProp.itemList.find((item) => item[itemProp.idKey] === itemId);
  if (!target) return <></>; // will happen after deletion

  if (itemType !== "PTeam") {
    console.assert(target.zones.filter((item) => item.zone_name === zone.zone_name));
  }

  const lastOne =
    itemType === "PTeam"
      ? false // pteam does not care about having empty zones
      : target.zones.length === 1;
  const maxlen = 32;
  const targetDesc =
    target[itemProp.nameKey].slice(0, maxlen) +
    (target[itemProp.nameKey].length > maxlen ? "..." : "");
  const confirmMessage = lastOne ? (
    <Typography align="center">
      Are you sure you want to delete this {itemType}: <b> {targetDesc} </b>?
      <br />
      This {itemType} has no other zones assigned, so{" "}
      <u>
        the <b> {itemType} </b> itself will be deleted
      </u>
      .
    </Typography>
  ) : (
    <Typography align="center">
      Are you sure you want to remove this {itemType}: <b> {targetDesc} </b>
      from zone: <b> {zone.zone_name} </b>?
      <br />
      The execution result will change the viewing authority.
    </Typography>
  );

  const processDeletion =
    itemType === "action"
      ? lastOne
        ? () => deleteAction(itemId)
        : () =>
            updateAction(itemId, {
              ...target,
              zone_names: target.zones
                .map((item) => item.zone_name)
                .filter((item) => item !== zone.zone_name),
            })
      : itemType === "topic"
        ? lastOne
          ? () => deleteTopic(itemId)
          : () =>
              updateTopic(itemId, {
                zone_names: target.zones
                  .map((item) => item.zone_name)
                  .filter((item) => item !== zone.zone_name),
              })
        : () => deleteZoneFromPTeam(zone.gteam_id, zone.zone_name, itemId);

  const handleDelete = async () => {
    await processDeletion()
      .then(async (response) => {
        const succeededMessage = lastOne
          ? `Delete ${itemType} succeeded`
          : `Remove ${itemType} from zone succeeded`;
        await Promise.all([
          dispatch(getGTeamZonesSummary(zone.gteam_id)),
          enqueueSnackbar(succeededMessage, { variant: "success" }),
        ]);
        onSetShow(false);
      })
      .catch((error) => {
        const resp = error.response ?? { status: "???", statusText: error.toString() };
        enqueueSnackbar(
          `Operation failed: ${resp.status} ${resp.statusText} - ${resp.data?.detail}`,
          { variant: "error" },
        );
      });
  };

  return (
    <>
      <Dialog
        onClose={handleClose}
        open={show}
        PaperProps={{ sx: { minWidth: "600px", maxWidth: "95%" } }}
      >
        <>
          <DialogTitle>
            <Typography variant="inherit">Confirm</Typography>
          </DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column">
              {confirmMessage}
              <Box display="flex">
                <Box flexGrow={1} />
                <Button onClick={() => onSetShow(false)} sx={{ ...modalCommonButtonStyle, mt: 1 }}>
                  Cancel
                </Button>
                <Button
                  onClick={handleDelete}
                  sx={{ ...modalCommonButtonStyle, ml: 1, mt: 1, color: red[800] }}
                >
                  Delete
                </Button>
              </Box>
            </Box>
          </DialogContent>
        </>
      </Dialog>
    </>
  );
}
ZoneItemDeleteModal.propTypes = {
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
  zone: PropTypes.object.isRequired,
  itemType: PropTypes.string.isRequired,
  itemId: PropTypes.string.isRequired,
};

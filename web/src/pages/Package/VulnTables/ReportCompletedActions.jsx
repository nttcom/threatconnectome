import { Close as CloseIcon } from "@mui/icons-material";
import {
  Box,
  Button,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  TextField,
  Typography,
  MenuItem,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import { useSnackbar } from "notistack";
import PropTypes from "prop-types";
import { useState } from "react";

import { ActionTypeIcon } from "../../../components/ActionTypeIcon";
import dialogStyle from "../../../cssModule/dialog.module.css";
import { useSkipUntilAuthUserIsReady } from "../../../hooks/auth";
import {
  useCreateActionLogMutation,
  useUpdateTicketStatusMutation,
  useGetUserMeQuery,
} from "../../../services/tcApi";
import { APIError } from "../../../utils/APIError";
import { errorToString } from "../../../utils/func";
import { ActionTypeChip } from "../ActionTypeChip";
import { RecommendedStar } from "../RecommendedStar";

export function ReportCompletedActions(props) {
  const {
    pteamId,
    serviceId,
    ticketId,
    vulnId,
    packageId,
    actionByFixedVersions,
    vulnActions,
    onSetShow,
    show,
  } = props;

  const [note, setNote] = useState("");
  const [selectedAction, setSelectedAction] = useState([]);
  const [activeStep, setActiveStep] = useState(0);
  const [skipped, setSkipped] = useState(new Set());

  const { enqueueSnackbar } = useSnackbar();

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: userMe,
    error: userMeError,
    isLoading: userMeIsLoading,
  } = useGetUserMeQuery(undefined, { skip });
  const [createActionLog] = useCreateActionLogMutation();
  const [updateTicketStatus] = useUpdateTicketStatusMutation();

  if (skip) return <></>;
  if (userMeError) throw new APIError(errorToString(userMeError), { api: "getUserMe" });
  if (userMeIsLoading) return <>Now loading UserInfo...</>;

  const actions = [actionByFixedVersions, ...vulnActions];

  const handleAction = async () =>
    await Promise.all(
      selectedAction.map(async (actionId) => {
        const action = actions.find((action) => action.action_id === actionId);
        if (!action) {
          console.error(`Action with ID ${actionId} not found in actions array.`);
          return;
        }

        const isActionByFixedVersions = actionByFixedVersions.action_id === actionId;

        return await createActionLog({
          action_id: isActionByFixedVersions ? null : action.action_id,
          action: action.action,
          action_type: action.action_type,
          recommended: action.recommended,
          pteam_id: pteamId,
          service_id: serviceId,
          ticket_id: ticketId,
          vuln_id: vulnId,
          user_id: userMe.user_id,
        })
          .unwrap()
          .then((data) => {
            enqueueSnackbar("Action succeeded", { variant: "success" });
            return data;
          });
      }),
    )
      .then(
        async (actionLogs) =>
          await updateTicketStatus({
            pteamId,
            ticketId,
            data: {
              ticket_handling_status: "completed",
              logging_ids: actionLogs.map((log) => log.logging_id),
              note: note.trim() || null,
              scheduled_at: null, // clear scheduled date
            },
          }).unwrap(),
      )
      .then((data) => {
        handleClose();
        setNote("");
        enqueueSnackbar("Set ticketstatus 'completed' succeeded", { variant: "success" });
      })
      .catch((error) =>
        enqueueSnackbar(`Operation failed: ${errorToString(error)}`, { variant: "error" }),
      );

  if (!pteamId || !serviceId || !ticketId || !vulnId || !packageId || !vulnActions) return <></>;

  const handleClose = () => {
    onSetShow(false);
  };

  const handleSelectAction = async (actionId) => {
    if (!actionId) {
      if (selectedAction.length) setSelectedAction([]);
      else setSelectedAction(vulnActions.map((action) => action.action_id));
    } else {
      if (selectedAction.includes(actionId))
        selectedAction.splice(selectedAction.indexOf(actionId), 1);
      else selectedAction.push(actionId);
      setSelectedAction([...selectedAction]);
    }
  };

  const isStepSkipped = (step) => {
    return skipped.has(step);
  };

  const handleNext = () => {
    let newSkipped = skipped;
    if (isStepSkipped(activeStep)) {
      newSkipped = new Set(newSkipped.values());
      newSkipped.delete(activeStep);
    }
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
    setSkipped(newSkipped);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  return (
    <Dialog open={show} onClose={handleClose} fullWidth>
      <DialogTitle>
        <Box alignItems="center" display="flex" flexDirection="row">
          {activeStep === 0 && (
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              Select the actions you have completed
            </Typography>
          )}
          {activeStep === 1 && (
            <Typography flexGrow={1} className={dialogStyle.dialog_title}>
              (Optional): Enter evidence of completion
            </Typography>
          )}
          <IconButton onClick={handleClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      <DialogContent>
        {activeStep === 0 && (
          <>
            {actions.length === 0 ? (
              <Box display="flex" flexDirection="row" alignItems="center" sx={{ color: grey[500] }}>
                <Typography variant="body2">No action</Typography>
              </Box>
            ) : (
              <>
                {actions.map((action) => (
                  <MenuItem
                    key={action.action_id}
                    onClick={() => handleSelectAction(action.action_id)}
                    selected={selectedAction.includes(action.action_id)}
                    sx={{
                      alignItems: "center",
                      display: "flex",
                      flexDirection: "row",
                    }}
                  >
                    <ActionTypeIcon
                      disabled={!action.recommended}
                      actionType={action.action_type}
                    />
                    <Box display="flex" flexDirection="column">
                      <Typography noWrap variant="body" width={400}>
                        {action.action}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </>
            )}
          </>
        )}
        {activeStep === 1 && (
          <>
            {actions
              .filter((action) => selectedAction.includes(action.action_id))
              .map((action) => (
                <Box
                  alignItems="center"
                  display="flex"
                  flexDirection="row"
                  key={action.action_id}
                  mb={1}
                >
                  <ActionTypeChip actionType={action.action_type} />
                  <RecommendedStar disabled={!action.recommended} />
                  <Box display="flex" flexDirection="column">
                    <Typography>{action.action}</Typography>
                  </Box>
                </Box>
              ))}
            <TextField
              fullWidth
              multiline
              onChange={(event) => setNote(event.target.value)}
              placeholder={
                "Evidence that you have completed the action, such as a report URL, " +
                "event logs, file hashes, etc."
              }
              variant="outlined"
              value={note}
            />
          </>
        )}
        <Box sx={{ display: "flex", flexDirection: "row", pt: 2 }}>
          {activeStep === 0 ? (
            <>
              <Box sx={{ flex: "1 1 auto" }} />
              <Button
                onClick={handleNext}
                className={dialogStyle.submit_btn}
                disabled={selectedAction.length === 0}
              >
                {`Done ${selectedAction.length}`}
              </Button>
            </>
          ) : (
            <>
              <Button
                onClick={handleBack}
                className={dialogStyle.submit_btn}
                disabled={activeStep === 0}
                sx={{ ml: -2 }}
              >
                Back
              </Button>
              <Box sx={{ flex: "1 1 auto" }} />
              <Button onClick={handleAction} className={dialogStyle.submit_btn}>
                Submit
              </Button>
            </>
          )}
        </Box>
      </DialogContent>
    </Dialog>
  );
}

ReportCompletedActions.propTypes = {
  pteamId: PropTypes.string.isRequired,
  serviceId: PropTypes.string.isRequired,
  ticketId: PropTypes.string.isRequired,
  vulnId: PropTypes.string.isRequired,
  packageId: PropTypes.string.isRequired,
  actionByFixedVersions: PropTypes.object.isRequired,
  vulnActions: PropTypes.array.isRequired,
  onSetShow: PropTypes.func.isRequired,
  show: PropTypes.bool.isRequired,
};

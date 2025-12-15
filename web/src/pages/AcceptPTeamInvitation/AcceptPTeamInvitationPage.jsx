import { Box, Button, Typography } from "@mui/material";
import { useSnackbar } from "notistack";
import { useLocation, useNavigate } from "react-router-dom";

import { useSkipUntilAuthUserIsReady } from "../../hooks/auth";
import { useApplyPTeamInvitationMutation, useGetPTeamInvitationQuery } from "../../services/tcApi";
import { APIError } from "../../utils/APIError";
import { commonButtonStyle } from "../../utils/const";
import { errorToString } from "../../utils/func";

export function AcceptPTeamInvitation() {
  const { enqueueSnackbar } = useSnackbar();

  const [applyPTeamInvitation] = useApplyPTeamInvitationMutation();

  const navigate = useNavigate();

  const params = new URLSearchParams(useLocation().search);
  const tokenId = params.get("token");

  const skip = useSkipUntilAuthUserIsReady();
  const {
    data: detail,
    error: detailError,
    isLoading: detailIsLoading,
  } = useGetPTeamInvitationQuery({ path: { invitation_id: tokenId } }, { skip });

  if (skip) return <></>;
  if (detailError)
    throw new APIError("This invitation is invalid or already expired.", {
      api: "getPTeamInvitation",
    });
  if (detailIsLoading) return <>Now loading user info...</>;

  const handleAccept = async (event) => {
    event.preventDefault();
    async function onSuccess(success) {
      enqueueSnackbar(`Now you are a member of '${detail.pteam_name}'`, { variant: "info" });
      params.delete("token");
      params.set("pteamId", detail.pteam_id);
      navigate("/pteam?" + params.toString());
    }
    function onError(error) {
      enqueueSnackbar(`Accepting invitation failed: ${errorToString(error)}`, { variant: "error" });
    }
    await applyPTeamInvitation({ body: { invitation_id: tokenId } })
      .unwrap()
      .then((success) => onSuccess(success))
      .catch((error) => onError(error));
  };

  return (
    <>
      <Typography variant="h6">Do you accept the invitation to the team below?</Typography>
      <Typography>Team Name: {detail.pteam_name}</Typography>
      <Typography>Team ID: {detail.pteam_id}</Typography>
      <Typography>
        Invitation created by {detail.email} ({detail.user_id})
      </Typography>
      <Box display="flex" flexDirection="row">
        <Button onClick={handleAccept} disabled={!detail.pteam_id} sx={commonButtonStyle}>
          Accept
        </Button>
      </Box>
    </>
  );
}

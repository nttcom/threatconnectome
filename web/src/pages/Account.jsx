import {
  Edit as EditIcon,
  MilitaryTech as MilitaryTechIcon,
  Save as SaveIcon,
  Star as StarIcon,
  Undo as UndoIcon,
  Verified as VerifiedIcon,
} from "@mui/icons-material";
import {
  Avatar,
  Badge,
  Box,
  Button,
  ButtonGroup,
  Divider,
  MenuItem,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

import UUIDTypography from "../components/UUIDTypography";
import { getAchievements, updateUser } from "../slices/user";
import { difficultyColors } from "../utils/const";

export default function Account() {
  const [editInfo, setEditInfo] = useState({
    years: 0,
  });
  const [editMode, setEditMode] = useState(false);

  const dispatch = useDispatch();
  const user = useSelector((state) => state.user.user);
  const achievements = useSelector((state) => state.user.achievements);

  useEffect(() => {
    if (!user?.user_id) return;
    setEditInfo({ years: user.years });
  }, [dispatch, user]);

  useEffect(() => {
    if (!user.user_id) return;
    if (!achievements) dispatch(getAchievements(user.user_id));
  }, [achievements, dispatch, user]);

  const handleChangeFavoriteBadge = (badgeId) => {
    dispatch(
      updateUser({
        userId: user.user_id,
        user: {
          favorite_badge: user.favorite_badge === badgeId ? "" : badgeId,
        },
      })
    );
  };

  const handleEditMode = () => {
    setEditInfo({ years: user.years });
    setEditMode(!editMode);
  };

  const handleSave = async () => {
    dispatch(
      updateUser({
        userId: user.user_id,
        user: { years: editInfo.years },
      })
    );
    handleEditMode();
  };

  return (
    user && (
      <>
        <Box display="flex" flexDirection="row" flexGrow={1} mb={1}>
          <Box display="flex" flexDirection="column" flexGrow={1}>
            <Box alignItems="baseline" display="flex" flexDirection="row">
              <Typography variant="h4">{user.email?.split("@")[0]}</Typography>
              <Typography color={grey[500]} variant="subtitle">
                {`@${user.email?.split("@")[1]}`}
              </Typography>
            </Box>
            <UUIDTypography>{user.user_id}</UUIDTypography>
          </Box>
          <Box justifyContent="center" display="flex" flexDirection="column">
            <ButtonGroup>
              {editMode && (
                <Tooltip arrow placement="bottom-end" title="Save">
                  <Button color="success" onClick={handleSave} variant="contained">
                    <SaveIcon />
                  </Button>
                </Tooltip>
              )}
              <Tooltip
                arrow
                placement="bottom-end"
                title={editMode ? "Exit Edit Mode" : "Edit Account Info"}
              >
                <Button color="warning" onClick={handleEditMode} variant="contained">
                  {editMode ? <UndoIcon /> : <EditIcon />}
                </Button>
              </Tooltip>
              <Tooltip arrow placement="bottom-end" title={"Request New Badge"}>
                <Button color="secondary" variant="contained">
                  <MilitaryTechIcon />
                </Button>
              </Tooltip>
            </ButtonGroup>
          </Box>
        </Box>
        <Divider />
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>Email:</Typography>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            <Typography>{user.email}</Typography>
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>User ID:</Typography>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            <Typography>{user.user_id}</Typography>
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" my={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>PTeam:</Typography>
          </Box>
          <Box display="flex" flexDirection="column" width="70%">
            {user.pteams?.length >= 1 ? (
              user.pteams.map((pteam, index) => (
                <Box alignItems="baseline" display="flex" flexDirection="row" key={index}>
                  <Typography mr={1}>{pteam.pteam_name}</Typography>
                  <UUIDTypography>{pteam.pteam_id}</UUIDTypography>
                </Box>
              ))
            ) : (
              <Typography>-</Typography>
            )}
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" my={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>ATeam:</Typography>
          </Box>
          <Box display="flex" flexDirection="column" width="70%">
            {user.ateams?.length >= 1 ? (
              user.ateams.map((ateam, index) => (
                <Box alignItems="baseline" display="flex" flexDirection="row" key={index}>
                  <Typography mr={1}>{ateam.ateam_name}</Typography>
                  <UUIDTypography>{ateam.ateam_id}</UUIDTypography>
                </Box>
              ))
            ) : (
              <Typography>-</Typography>
            )}
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" my={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>GTeam:</Typography>
          </Box>
          <Box display="flex" flexDirection="column" width="70%">
            {user.gteams?.length >= 1 ? (
              user.gteams.map((gteam, index) => (
                <Box alignItems="baseline" display="flex" flexDirection="row" key={index}>
                  <Typography mr={1}>{gteam.gteam_name}</Typography>
                  <UUIDTypography>{gteam.gteam_id}</UUIDTypography>
                </Box>
              ))
            ) : (
              <Typography>-</Typography>
            )}
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Tooltip
              arrow
              title="Please select years of your work experience in security to support security response."
            >
              <Typography>Years of work experience in security:</Typography>
            </Tooltip>
          </Box>
          <Box display="flex" flexDirection="row" width="70%">
            {editMode ? (
              <TextField
                fullWidth
                label="Years of work experience in security:"
                margin="dense"
                onChange={(event) => setEditInfo({ ...editInfo, years: event.target.value })}
                select
                size="small"
                value={editInfo.years}
              >
                <MenuItem value={0}>0+ year</MenuItem>
                <MenuItem value={2}>2+ years</MenuItem>
                <MenuItem value={5}>5+ years</MenuItem>
                <MenuItem value={7}>7+ years</MenuItem>
              </TextField>
            ) : (
              <Typography>
                {user.years}+ year{user.years <= 1 ? "" : "s"}
              </Typography>
            )}
          </Box>
        </Box>
        <Box alignItems="center" display="flex" flexDirection="row" mt={1}>
          <Box display="flex" flexDirection="row" width="30%">
            <Typography>Achievements:</Typography>
          </Box>
          <Box display="flex" flexDirection="row" flexWrap="wrap" width="70%">
            {achievements?.map((achievement, index) => (
              <Tooltip
                arrow
                describeChild
                key={index}
                onClick={() => handleChangeFavoriteBadge(achievement.badge_id)}
                placement="bottom-start"
                title={`${achievement.badge_name}${
                  achievement.badge_id === user.favorite_badge ? " *" : ""
                }`}
                sx={{ mr: 1 }}
              >
                <Badge
                  anchorOrigin={{
                    horizontal: "right",
                    vertical: "bottom",
                  }}
                  badgeContent={<StarIcon color="warning" />}
                  invisible={achievement.badge_id !== user.favorite_badge}
                  overlap="circular"
                >
                  <Avatar
                    alt={achievement.badge_name.slice(0, 1)}
                    src={achievement.image_url}
                    variant="square"
                    sx={{
                      border: 2,
                      borderColor: difficultyColors[achievement.difficulty],
                    }}
                  >
                    {/* default badge image */}
                    {achievement.image_url ? "" : <VerifiedIcon />}
                  </Avatar>
                </Badge>
              </Tooltip>
            ))}
          </Box>
        </Box>
      </>
    )
  );
}

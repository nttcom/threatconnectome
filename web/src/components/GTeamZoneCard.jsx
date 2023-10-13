import {
  Box,
  Card,
  CardActionArea,
  CardContent,
  Divider,
  Typography,
  Table,
  TableBody,
  TableRow,
  TableCell,
} from "@mui/material";
import { grey } from "@mui/material/colors";
import PropTypes from "prop-types";
import React from "react";
import { useLocation, useNavigate } from "react-router";

import { calcTimestampDiff } from "../utils/func";

function textTrim(selector) {
  const maxWordCount = 48;
  const clamp = "…";
  if (selector.length > maxWordCount) {
    selector = selector.substr(0, maxWordCount - 1) + clamp; // remove 1 character
  }
  return selector;
}

export default function GTeamZoneCard(props) {
  const { zones, archived } = props;
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  if (!zones) return <></>;
  return (
    <>
      <Box display="flex" flexWrap="wrap" sx={{ margin: -1.5 }}>
        {zones.map((zone) => (
          <Card
            variant="outlined"
            sx={{
              margin: 1,
              width: "48%",
              border: "solid grey 0.5px",
              bgcolor: archived ? grey[200] : undefined,
            }}
            key={zone.zone_name}
          >
            <CardActionArea onClick={() => navigate(`./${zone.zone_name}?${params.toString()}`)}>
              <Box sx={{ height: "110px", margin: 0 }}>
                <Box display="flex" sx={{ height: "75%" }}>
                  <Typography
                    className="zoneName"
                    variant="h6"
                    component="div"
                    flexWrap="wrap"
                    sx={{
                      padding: "18px 18px 0px",
                      wordBreak: "break-word",
                      color: archived ? grey[500] : undefined,
                    }}
                  >
                    {textTrim(zone.zone_name)}
                  </Typography>
                  <Box flexGrow={1} />
                </Box>
                <Typography sx={{ fontSize: 14, pl: "15px", pb: "10px" }} color="text.secondary">
                  last Activity: {calcTimestampDiff(zone.topics[0]?.updated_at)}
                </Typography>
              </Box>
              <CardContent sx={{ padding: 0 }}>
                <Divider variant="middle" sx={{ border: "solid 0.5px" }} />
                <Typography variant="body2" sx={{ wordBreak: "break-word", padding: "18px" }}>
                  {zone.zone_info}
                </Typography>
                <Table sx={{ maxWidth: "95%", margin: "18px" }} aria-label="simple table">
                  <TableBody>
                    <TableRow>
                      <TableCell
                        component="th"
                        sx={{ width: "5%", bgcolor: archived ? grey[200] : grey[100] }}
                      >
                        <Typography variant="subtitle1">Pteams</Typography>
                      </TableCell>
                      <TableCell component="th" sx={{ width: "40%", wordBreak: "break-word" }}>
                        {zone.pteams.length >= 1
                          ? zone.pteams
                              .map((pteam) => pteam.pteam_name)
                              .sort((a, b) => a.localeCompare(b)) // alphabetically
                              .slice(0, 3) // extract top 3
                              .join(",")
                          : "-"}
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ padding: "10px" }}>
                      <TableCell
                        component="th"
                        sx={{ width: "5%", bgcolor: archived ? grey[200] : grey[100] }}
                      >
                        <Typography variant="subtitle1" sx={{ overflowWrap: "anywhere" }}>
                          Topic
                        </Typography>
                      </TableCell>
                      <TableCell component="th" sx={{ width: "40%", wordBreak: "break-word" }}>
                        {/* 0th topic is latest */}
                        {zone.topics[0] ? zone.topics[0].title : "-"}
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Box>
    </>
  );
}

GTeamZoneCard.propTypes = {
  zones: PropTypes.array,
  archived: PropTypes.bool,
};

GTeamZoneCard.defaultProps = {
  archived: false,
};

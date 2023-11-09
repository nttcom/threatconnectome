import { Box, Chip } from "@mui/material";
import { grey } from "@mui/material/colors";
import React, { useState } from "react";

const groupList = [
  {
    id: 1,
    name: "flashsence",
  },
  {
    id: 2,
    name: "misp-server",
  },
  {
    id: 3,
    name: "threatconnectome",
  },
];

export default function PTeamGroupList() {
  const [selectedGroup, setSelectedGroup] = useState("");

  const handleSelectGroup = (group) => {
    if (selectedGroup === group) {
      setSelectedGroup("");
    } else {
      setSelectedGroup(group);
    }
  };

  return (
    <>
      <Box>
        {groupList.map((group) => (
          <Chip
            key={group.id}
            label={group.name}
            variant={group === selectedGroup ? "" : "outlined"}
            sx={{
              mt: 1,
              borderRadius: "2px",
              border: `1px solid ${grey[300]}`,
              borderLeft: `5px solid ${grey[300]}`,
              mr: 1,
              background: group === selectedGroup ? grey[400] : "",
            }}
            onClick={() => {
              handleSelectGroup(group);
            }}
          />
        ))}
      </Box>
    </>
  );
}

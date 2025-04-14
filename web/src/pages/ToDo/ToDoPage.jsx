import { Typography } from "@mui/material";
import Box from "@mui/material/Box";
import React from "react";

import { Android12Switch } from "../../components/Android12Switch";

import { ToDoTable } from "./ToDoTable";

export function ToDo() {
  return (
    <>
      <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
        <Android12Switch />
        <Typography>My tasks</Typography>
      </Box>
      <ToDoTable />
    </>
  );
}

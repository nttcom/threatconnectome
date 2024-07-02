import { UploadFile } from "@mui/icons-material";
import { Tab, Tabs } from "@mui/material";
import { grey } from "@mui/material/colors";
import React from "react";

export const StatusTabsAllServices = () => {
  return (
    <Tabs value={0}>
      <Tab
        label="All"
        sx={{
          textTransform: "none",
          border: `1px solid ${grey[300]}`,
          borderRadius: "0.5rem 0.5rem 0 0",
          width: "10%",
          mt: 1,
        }}
      />
      <Tab
        icon={<UploadFile />}
        label="Upload"
        sx={{
          textTransform: "none",
          border: `1px solid ${grey[300]}`,
          borderRadius: "0.5rem 0.5rem 0 0",
          width: "10%",
          mt: 1,
        }}
      />
    </Tabs>
  );
};

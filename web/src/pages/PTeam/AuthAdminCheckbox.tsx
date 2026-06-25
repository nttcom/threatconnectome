import { Box, Checkbox } from "@mui/material";
import type { ChangeEvent } from "react";

type AuthAdminCheckboxProps = {
  checked: boolean;
  editable: boolean;
  modified: boolean;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
};

export function AuthAdminCheckbox(props: AuthAdminCheckboxProps) {
  const { checked, editable, modified, onChange } = props;

  return (
    <>
      <Box display="flex" flexDirection="row" alignItems="center" width="40px">
        <Checkbox
          checked={checked}
          disabled={!editable}
          onChange={editable ? onChange : undefined}
          size="small"
        />
        {modified && "*"}
      </Box>
    </>
  );
}

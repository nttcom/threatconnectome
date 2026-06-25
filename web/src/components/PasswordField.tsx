import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import { Tooltip, TextField, InputAdornment, IconButton } from "@mui/material";
import type { ChangeEvent } from "react";

type PasswordFieldProps = {
  name: string;
  label: string;
  value: string;
  edited: Set<string>;
  onChange: (event: ChangeEvent<HTMLInputElement>) => void;
  isVisible: boolean;
  onToggle: () => void;
  minLength?: number;
  tooltipTitle: string;
};

function isInputChangeEvent(
  event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
): event is ChangeEvent<HTMLInputElement> {
  return event.currentTarget instanceof HTMLInputElement;
}

export function PasswordField({
  name,
  label,
  value,
  edited,
  onChange,
  isVisible,
  onToggle,
  minLength = 8,
  tooltipTitle,
}: PasswordFieldProps) {
  const error = edited.has(name) && value.length < minLength;
  const handleChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (isInputChangeEvent(event)) {
      onChange(event);
    }
  };

  return (
    <Tooltip arrow placement="bottom-end" title={tooltipTitle}>
      <TextField
        autoComplete="new-password"
        error={error}
        fullWidth
        label={label}
        margin="normal"
        onChange={handleChange}
        required
        type={isVisible ? "text" : "password"}
        value={value}
        slotProps={{
          htmlInput: { minLength },
          input: {
            endAdornment: (
              <InputAdornment position="end">
                <IconButton onClick={onToggle} aria-label={`toggle ${name} visibility`}>
                  {isVisible ? <VisibilityOffIcon /> : <VisibilityIcon />}
                </IconButton>
              </InputAdornment>
            ),
          },
        }}
      />
    </Tooltip>
  );
}

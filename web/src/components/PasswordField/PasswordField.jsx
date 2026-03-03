import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
} from "@mui/icons-material";
import { Tooltip, TextField, InputAdornment, IconButton } from "@mui/material";
import PropTypes from "prop-types";

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
}) {
  const error = edited.has(name) && value.length < minLength;

  return (
    <Tooltip arrow placement="bottom-end" title={tooltipTitle}>
      <TextField
        autoComplete="new-password"
        error={error}
        fullWidth
        label={label}
        margin="normal"
        onChange={onChange}
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

PasswordField.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  edited: PropTypes.instanceOf(Set).isRequired,
  onChange: PropTypes.func.isRequired,
  isVisible: PropTypes.bool.isRequired,
  onToggle: PropTypes.func.isRequired,
  minLength: PropTypes.number,
  tooltipTitle: PropTypes.string.isRequired,
};
